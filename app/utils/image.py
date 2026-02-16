import httpx
from fastapi import UploadFile, HTTPException
from app.core.config import settings

async def upload_image_to_imgbb(file: UploadFile) -> str:
    """
    Uploads an image to IMGBB and returns the display URL.
    """
    if not settings.IMGBB_API_KEY:
        raise HTTPException(status_code=500, detail="IMGBB API Key not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            file_content = await file.read()
            files = {"image": (file.filename, file_content, file.content_type)}
            data = {"key": settings.IMGBB_API_KEY}
            
            response = await client.post("https://api.imgbb.com/1/upload", data=data, files=files)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                return result["data"]["url"]
            else:
                raise HTTPException(status_code=400, detail="Image upload failed")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
        finally:
            await file.seek(0)
