from typing import Optional, List
from datetime import time
from pydantic import BaseModel
from app.models.availability import StaffType, DayOfWeek

class AvailabilityBase(BaseModel):
    staff_type: StaffType
    staff_id: str
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityUpdate(BaseModel):
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class AvailabilityInDBBase(AvailabilityBase):
    id: str

    class Config:
        from_attributes = True

class Availability(AvailabilityInDBBase):
    pass

class AvailabilityBulkCreate(BaseModel):
    staff_ids: List[str]
    staff_type: StaffType
    days: List[DayOfWeek]
    start_time: time
    end_time: time
