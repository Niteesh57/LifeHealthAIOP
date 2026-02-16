from typing import Optional
from pydantic import BaseModel
from app.schemas.user import User

class DoctorBase(BaseModel):
    specialization: str
    license_number: str
    experience_years: Optional[int] = 0
    tags: Optional[str] = None
    is_available: Optional[bool] = True
    user_id: str
    hospital_id: str
    created_by: Optional[str] = None

class DoctorCreate(DoctorBase):
    hospital_id: Optional[str] = None

class DoctorRegister(BaseModel):
    user_search_query: str  # Email or Compact ID
    specialization: str
    license_number: str
    experience_years: Optional[int] = 0
    tags: Optional[str] = None

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    tags: Optional[str] = None
    is_available: Optional[bool] = None

class DoctorInDBBase(DoctorBase):
    id: str

    class Config:
        from_attributes = True

class DoctorResponse(DoctorInDBBase):
    user: Optional[User] = None
    pass
