import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class LabSeverity(str, enum.Enum):
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"

class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_url = Column(String, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    summary = Column(String, nullable=True)
    severity = Column(String, default=LabSeverity.NORMAL.value)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    appointments = relationship("Appointment", back_populates="lab_report")
