import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Floor(Base):
    __tablename__ = "floors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    floor_number = Column(String)
    direction_notes = Column(String, nullable=True)
    unique_identifier = Column(String, unique=True, index=True)
    hospital_id = Column(String, ForeignKey("hospitals.id"), nullable=False)

    # Relationships
    hospital = relationship("Hospital", back_populates="floors")
