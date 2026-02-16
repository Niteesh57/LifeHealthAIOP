import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    hospital_id = Column(String, ForeignKey("hospitals.id"), nullable=False)
    specialization = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    experience_years = Column(Integer, default=0)
    tags = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="doctor_profile", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    hospital = relationship("Hospital", back_populates="doctors")
    patients = relationship("Patient", back_populates="assigned_doctor")
