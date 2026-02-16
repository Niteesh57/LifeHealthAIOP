from app.crud.base import CRUDBase
from app.models.lab_report import LabReport
from app.schemas.lab_report import LabReportCreate, LabReportUpdate

class CRUDLabReport(CRUDBase[LabReport, LabReportCreate, LabReportUpdate]):
    pass

lab_report = CRUDLabReport(LabReport)
