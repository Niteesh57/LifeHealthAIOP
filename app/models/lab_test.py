import uuid
from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    available = Column(Boolean, default=True)
    hospital_id = Column(String, ForeignKey("hospitals.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    hospital = relationship("Hospital", back_populates="lab_tests")
    creator = relationship("User", foreign_keys=[created_by])
