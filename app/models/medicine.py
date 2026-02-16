import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class InventoryChangeType(str, enum.Enum):
    ADDED = "added"
    REMOVED = "removed"

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    unique_code = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    quantity = Column(Integer, default=0)
    price = Column(Float)
    hospital_id = Column(String, ForeignKey("hospitals.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    hospital = relationship("Hospital", back_populates="medicines")
    logs = relationship("InventoryLog", back_populates="medicine")
    creator = relationship("User", foreign_keys=[created_by])

class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    medicine_id = Column(String, ForeignKey("medicines.id"), nullable=False)
    change_type = Column(String)  # added / removed
    quantity_changed = Column(Integer)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    medicine = relationship("Medicine", back_populates="logs")
