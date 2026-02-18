from typing import TypedDict, Annotated, Sequence, Union
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import logging
import io
import httpx
from PIL import Image

from app.agent.LLM.llm import get_vqa_chain
from app.utils.pdf import extract_text_from_pdf_url

logger = logging.getLogger(__name__)

# State Definition
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    document_url: str
    document_type: str # 'pdf' or 'image'
    extracted_text: str # For PDFs
    local_image_path: str # For Images (downloaded temp path)
    
# Nodes
async def load_document(state: AgentState):
    """
    Downloads document from URL. Detects type.
    If PDF: Extract text.
    If Image: Download to temp file.
    """
    url = state["document_url"]
    logger.info(f"Loading document: {url}")
    
    # Simple extension check (improve with checking content-type header if needed)
    lower_url = url.lower()
    
    if ".pdf" in lower_url:
        text = await extract_text_from_pdf_url(url)
        return {"document_type": "pdf", "extracted_text": text}
    else:
        # Assume Image
        # Download to temp file for MedVQA to read
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            image_bytes = resp.content
            
        import tempfile, os
        fd, path = tempfile.mkstemp(suffix=".jpg") # MedVQA might expect extension
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(image_bytes)
            
        return {"document_type": "image", "local_image_path": path}

async def analyze_document(state: AgentState):
    """
    Calls MedVQA with the document context.
    """
    llm = get_vqa_chain()
    
    # Get the latest question
    question = state["messages"][-1].content
    
    response_text = ""
    
    if state.get("document_type") == "pdf":
        # Text Context
        context = state.get("extracted_text", "")
        # Limit context size if needed? MedGemma has 8k context probably.
        prompt = f"System: You are an expert medical AI. Analyze the following medical report text and answer the user's question.\n\nReport Context:\n{context[:6000]}\n\nUser Question: {question}"
        
        response_text = llm.answer_question(question=prompt, image_path=None)
        
    else:
        # Image Context
        path = state.get("local_image_path")
        if not path:
             return {"messages": [HumanMessage(content="Error: Image not found.")]}
             
        # "Describe this image" is default if question is empty, but we have question.
        response_text = llm.answer_question(question=question, image_path=path)
        
        # Cleanup temp file? Maybe later or rely on OS cleanup
        try:
            import os
            os.remove(path)
        except: pass

    return {"messages": [HumanMessage(content=response_text)]}

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("load_document", load_document)
workflow.add_node("analyze_document", analyze_document)

workflow.set_entry_point("load_document")
workflow.add_edge("load_document", "analyze_document")
workflow.add_edge("analyze_document", END)

checkpointer = MemorySaver()

app = workflow.compile(checkpointer=checkpointer)

async def analyze_medical_document(user_id: str, document_url: str, question: str):
    """
    Entry point to run the agent. Returns a stream of tokens/messages if possible, 
    or the final string.
    """
    inputs = {
        "messages": [HumanMessage(content=question)],
        "document_url": document_url,
        "document_type": "", # will be filled by load_document
        "extracted_text": "",
        "local_image_path": ""
    }
    
    config = {"configurable": {"thread_id": user_id}}
    
    # Run the graph
    # To support streaming, we need the LLM to stream. 
    # MedVQA.answer_question() currently waits for full generation.
    # We can stream the *graph events*, but the LLM node is the bottleneck.
    # For now, we await the result. Refactoring MedVQA for true token streaming 
    # requires TextIteratorStreamer in transformers generate().
    
    result = await app.ainvoke(inputs, config=config)
    return result["messages"][-1].content
