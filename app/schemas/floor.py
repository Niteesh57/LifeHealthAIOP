from typing import Optional
from pydantic import BaseModel

class FloorBase(BaseModel):
    floor_number: str
    direction_notes: Optional[str] = None
    unique_identifier: str
    hospital_id: str

class FloorCreate(FloorBase):
    pass

class FloorUpdate(BaseModel):
    floor_number: Optional[str] = None
    direction_notes: Optional[str] = None
    unique_identifier: Optional[str] = None

class FloorInDBBase(FloorBase):
    id: str

    class Config:
        from_attributes = True

class Floor(FloorInDBBase):
    pass
