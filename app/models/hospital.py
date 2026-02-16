import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    license_number = Column(String, unique=True, index=True)
    specialization = Column(String, nullable=True)  # Keeping as string per spec, but could link to Specialization
    address = Column(String)
    description = Column(Text, nullable=True)
    admin_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", back_populates="hospital")
    doctors = relationship("Doctor", back_populates="hospital")
    nurses = relationship("Nurse", back_populates="hospital")
    patients = relationship("Patient", back_populates="hospital")
    medicines = relationship("Medicine", back_populates="hospital")
    lab_tests = relationship("LabTest", back_populates="hospital")
    floors = relationship("Floor", back_populates="hospital")
