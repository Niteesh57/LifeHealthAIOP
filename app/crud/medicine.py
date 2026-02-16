from app.crud.base import CRUDBase
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineUpdate

class CRUDMedicine(CRUDBase[Medicine, MedicineCreate, MedicineUpdate]):
    pass

medicine = CRUDMedicine(Medicine)
