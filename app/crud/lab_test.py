from app.crud.base import CRUDBase
from app.models.lab_test import LabTest
from app.schemas.lab_test import LabTestCreate, LabTestUpdate

class CRUDLabTest(CRUDBase[LabTest, LabTestCreate, LabTestUpdate]):
    pass

lab_test = CRUDLabTest(LabTest)
