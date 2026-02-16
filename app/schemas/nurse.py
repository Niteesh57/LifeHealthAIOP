from typing import Optional
from pydantic import BaseModel
from app.models.nurse import ShiftType
from app.schemas.user import User

class NurseBase(BaseModel):
    shift_type: ShiftType = ShiftType.DAY
    is_available: Optional[bool] = True
    user_id: str
    hospital_id: str
    created_by: Optional[str] = None

class NurseCreate(NurseBase):
    hospital_id: Optional[str] = None

class NurseRegister(BaseModel):
    user_search_query: str  # Email or Compact ID
    shift_type: ShiftType = ShiftType.DAY

class NurseUpdate(BaseModel):
    shift_type: Optional[ShiftType] = None
    is_available: Optional[bool] = None

class NurseInDBBase(NurseBase):
    id: str

    class Config:
        from_attributes = True

class NurseResponse(NurseInDBBase):
    user: Optional[User] = None
    pass
