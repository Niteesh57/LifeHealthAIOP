import uuid
import mimetypes
from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def upload_file_to_supabase(file: UploadFile, bucket_name: str = None) -> str:
    """
    Uploads a file to Supabase Storage and returns the public URL.
    """
    try:
        supabase = get_supabase_client()
        bucket_name = bucket_name or settings.SUPABASE_BUCKET
        
        # Generate unique filename
        file_ext = mimetypes.guess_extension(file.content_type) or ".jpg"
        if not file.filename.endswith(file_ext):
            filename = f"{uuid.uuid4()}{file_ext}"
        else:
            filename = f"{uuid.uuid4()}-{file.filename}"
            
        # Read file content
        file_content = await file.read()
        
        # Upload to Supabase
        # Supabase-py storage upload expects bytes
        res = supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        # Get Public URL
        # Supabase-py might return a response object or raise error
        # Assuming upload successful if no error raised (or check res)
        
        public_url_res = supabase.storage.from_(bucket_name).get_public_url(filename)
        
        # get_public_url returns a string in older versions, or a response? 
        # Checking docs: it returns a string URL usually.
        
        return public_url_res
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        await file.seek(0)

# Alias for backward compatibility if needed, or preferred name
upload_image = upload_file_to_supabase
upload_file = upload_file_to_supabase
