from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PatientBase(BaseModel):
    full_name: str
    age: int
    gender: str
    phone: Optional[str] = None
    hospital_id: str
    assigned_doctor_id: Optional[str] = None

class PatientCreate(PatientBase):
    email: str  # Required for auto-creating user account
    password: Optional[str] = "Patient@123"  # Default password


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    assigned_doctor_id: Optional[str] = None

class PatientInDBBase(PatientBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Patient(PatientInDBBase):
    pass
