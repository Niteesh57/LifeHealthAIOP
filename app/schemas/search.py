from typing import List, Optional, Any
from pydantic import BaseModel
from app.schemas.doctor import DoctorResponse
from app.schemas.nurse import NurseResponse
from app.schemas.medicine import Medicine
from app.schemas.lab_test import LabTest

class UnifiedSearchResult(BaseModel):
    doctors: List[DoctorResponse] = []
    nurses: List[NurseResponse] = []
    medicines: List[Medicine] = []
    lab_tests: List[LabTest] = []
    users: List[Any] = [] # For staff addition search
