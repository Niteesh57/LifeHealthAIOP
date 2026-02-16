import uuid
from sqlalchemy import Column, String, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class StaffType(str, enum.Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"

class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    staff_type = Column(String, nullable=False)
    staff_id = Column(String, nullable=False, index=True)  # Can be doctor_id or nurse_id
    day_of_week = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
