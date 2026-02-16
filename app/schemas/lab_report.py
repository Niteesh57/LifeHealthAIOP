from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.lab_report import LabSeverity

class LabReportBase(BaseModel):
    pdf_url: str
    created_by: str
    summary: Optional[str] = None
    severity: LabSeverity = LabSeverity.NORMAL

class LabReportCreate(LabReportBase):
    pass

class LabReportUpdate(BaseModel):
    pdf_url: Optional[str] = None
    summary: Optional[str] = None
    severity: Optional[LabSeverity] = None

class LabReport(LabReportBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
