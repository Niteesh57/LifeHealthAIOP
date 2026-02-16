from typing import Optional
from pydantic import BaseModel

class LabTestBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    available: Optional[bool] = True
    hospital_id: str
    created_by: Optional[str] = None

class LabTestCreate(LabTestBase):
    pass

class LabTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None

class LabTestInDBBase(LabTestBase):
    id: str

    class Config:
        from_attributes = True

class LabTest(LabTestInDBBase):
    pass
