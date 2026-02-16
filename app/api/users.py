from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.user import user as crud_user
from app.schemas.user import User, UserUpdate
from app.models.user import User as UserModel, UserRole
import os
import httpx

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: UserModel = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user information.
    
    - Returns your user profile
    - Includes hospital association
    """
    return current_user

@router.get("/", response_model=List[User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Retrieve users.
    
    - **Admin only**: Requires hospital_admin role
    - **Hospital filtered**: Only shows users from your hospital
    - **Pagination**: Use skip/limit for pagination
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/upload-image")
async def upload_user_image(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Upload user profile image.
    
    - Uploads to ImgBB
    - Updates user profile with image URL
    """
    api_key = os.getenv("IMGBB_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="IMGBB_API_KEY not configured")
    
    contents = await file.read()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key},
            files={"image": contents}
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to upload image")
    
    data = response.json()
    image_url = data["data"]["url"]
    
    # Update user with image URL
    user_update = UserUpdate(image=image_url)
    updated_user = await crud_user.update(db, db_obj=current_user, obj_in=user_update)
    
    return {"image_url": image_url}
