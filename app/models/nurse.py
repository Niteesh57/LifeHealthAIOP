import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class ShiftType(str, enum.Enum):
    DAY = "day"
    NIGHT = "night"

class Nurse(Base):
    __tablename__ = "nurses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    hospital_id = Column(String, ForeignKey("hospitals.id"), nullable=False)
    shift_type = Column(String, default=ShiftType.DAY.value)
    is_available = Column(Boolean, default=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="nurse_profile", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    hospital = relationship("Hospital", back_populates="nurses")
