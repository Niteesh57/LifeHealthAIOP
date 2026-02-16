from typing import Optional
from pydantic import BaseModel

class HospitalBase(BaseModel):
    name: str
    license_number: str
    specialization: Optional[str] = None
    address: str
    description: Optional[str] = None
    admin_email: Optional[str] = None

class HospitalCreate(HospitalBase):
    pass

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    admin_email: Optional[str] = None

class HospitalInDBBase(HospitalBase):
    id: str

    class Config:
        from_attributes = True

class Hospital(HospitalInDBBase):
    pass
