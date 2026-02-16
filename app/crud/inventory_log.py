from app.crud.base import CRUDBase
from app.models.medicine import InventoryLog
from app.schemas.medicine import InventoryLogCreate, InventoryLogBase

class CRUDInventoryLog(CRUDBase[InventoryLog, InventoryLogCreate, InventoryLogBase]):
    pass

inventory_log = CRUDInventoryLog(InventoryLog)
