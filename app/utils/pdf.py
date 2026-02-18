import io
import httpx
from pypdf import PdfReader
from fastapi import HTTPException

async def extract_text_from_pdf_url(url: str) -> str:
    """
    Download PDF from URL and extract text using pypdf.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            pdf_bytes = io.BytesIO(response.content)
            
        reader = PdfReader(pdf_bytes)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {str(e)}")
