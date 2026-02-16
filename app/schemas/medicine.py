from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.medicine import InventoryChangeType

class InventoryLogBase(BaseModel):
    change_type: InventoryChangeType
    quantity_changed: int
    reason: Optional[str] = None

class InventoryLogCreate(InventoryLogBase):
    medicine_id: str

class InventoryLogInDB(InventoryLogBase):
    id: str
    medicine_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class MedicineBase(BaseModel):
    name: str
    unique_code: str
    description: Optional[str] = None
    quantity: int = 0
    price: float
    hospital_id: str
    created_by: Optional[str] = None

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class MedicineInDBBase(MedicineBase):
    id: str
    created_at: datetime
    updated_at: datetime
    # Note: logs relationship excluded to prevent lazy loading issues with async SQLAlchemy

    class Config:
        from_attributes = True

class Medicine(MedicineInDBBase):
    pass
