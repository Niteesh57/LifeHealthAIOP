from langchain_huggingface import HuggingFacePipeline
from transformers import AutoProcessor, AutoModelForCausalLM, AutoModel, pipeline
import torch
import os

# Local Model Paths
MEDASR_PATH = r"C:\xampp\htdocs\opik_Backend\medasr"
MEDGEMMA_PATH = r"C:\xampp\htdocs\opik_Backend\medgemma"
PATH_FOUNDATION_PATH = r"C:\xampp\htdocs\opik_Backend\path-foundation"
HEAR_PATH = r"C:\xampp\htdocs\opik_Backend\hear"

class MedVQA:
    def __init__(self):
        self.model_id = MEDGEMMA_PATH
        print(f"Loading MedVQA from {self.model_id}...")
        self.pipeline = None
        
        try:
            # Gemma 3 or similar VLMs commonly use 'image-text-to-text'
            self.pipeline = pipeline(
                "image-text-to-text",
                model=self.model_id,
                torch_dtype=torch.float16,
                device=0 if torch.cuda.is_available() else -1,
                trust_remote_code=True
            )
            print("MedVQA Model loaded.")
        except Exception as e:
            print(f"Warning: Could not load MedVQA from {self.model_id}. Check path. Error: {e}")

    def answer_question(self, question, image_path=None):
        if not self.pipeline: return "Model not loaded."
        
        # Construct messages for VLM pipeline
        content = []
        
        if image_path:
            from PIL import Image
            image = Image.open(image_path).convert("RGB")
            content.append({"type": "image", "image": image})
        
        content.append({"type": "text", "text": question})
        
        messages = [
            {
                "role": "user",
                "content": content
            }
        ]
        
        try:
            # Pipeline handles formatting/tokenization
            output = self.pipeline(messages, max_new_tokens=200)
            # Output format usually: [{'generated_text': ...}] 
            # or for chat pipeline: [{'generated_text': [{'role':..., 'content':...}]}] ?
            # User example: output[0]["generated_text"][-1]["content"]
            # Let's inspect output structure if it varies, but assuming user snippet is correct for this model type.
            
            generated_text = output[0]["generated_text"]
            # If it returns the full chat history, we take the last message content
            if isinstance(generated_text, list):
                return generated_text[-1]["content"]
            else:
                return generated_text
        except Exception as e:
            print(f"Inference Error: {e}")
            return f"Error processing request: {e}"

class PathFoundation:
    def __init__(self):
        self.model_id = PATH_FOUNDATION_PATH
        print(f"Loading PathFoundation from {self.model_id}...")
        try:
            self.model = AutoModel.from_pretrained(self.model_id, trust_remote_code=True, device_map="auto")
            print("PathFoundation loaded.")
        except Exception as e:
            print(f"Warning: Failed to load PathFoundation: {e}")

class HearModel:
    def __init__(self):
        self.model_id = HEAR_PATH
        print(f"Loading HeAR from {self.model_id}...")
        try:
            self.model = AutoModel.from_pretrained(self.model_id, trust_remote_code=True, device_map="auto")
            print("HeAR loaded.")
        except Exception as e:
            print(f"Warning: Failed to load HeAR: {e}")

class MedASR:
    def __init__(self):
        self.model_id = MEDASR_PATH
        self.pipeline = None
        print(f"Loading MedASR from {self.model_id}...")
        try:
             self.pipeline = pipeline(
                "automatic-speech-recognition", 
                model=self.model_id, 
                device=0 if torch.cuda.is_available() else -1,
                chunk_length_s=30,
                stride_length_s=5,
                trust_remote_code=True
            )
             print("MedASR Model loaded.")
        except Exception as e:
            print(f"Warning: Could not load MedASR from {self.model_id}: {e}")

    def transcribe(self, audio_input):
        if not self.pipeline: return ""
        return self.pipeline(audio_input)["text"]

# Singletons
llm_instance = None
path_instance = None
hear_instance = None
medasr_instance = None

def get_vqa_chain():
    global llm_instance
    if llm_instance is None:
        llm_instance = MedVQA()
    return llm_instance

def get_medasr_chain():
    global medasr_instance
    if medasr_instance is None:
        medasr_instance = MedASR()
    return medasr_instance

def get_path_foundation():
    global path_instance
    if path_instance is None:
        path_instance = PathFoundation()
    return path_instance

def get_hear_model():
    global hear_instance
    if hear_instance is None:
        hear_instance = HearModel()
    return hear_instance

