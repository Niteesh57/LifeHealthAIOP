from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.medicine import medicine as crud_medicine
from app.crud.inventory_log import inventory_log as crud_inventory_log
from app.schemas.medicine import Medicine, MedicineCreate, MedicineUpdate, InventoryLogCreate, InventoryChangeType
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Medicine)
async def create_medicine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    medicine_in: MedicineCreate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Create a new medicine in inventory.
    """
    # Ensure hospital_id matches current user's hospital
    if current_user.hospital_id:
        medicine_in.hospital_id = current_user.hospital_id
    
    # Set created_by to current user
    medicine_in.created_by = current_user.id
    
    medicine = await crud_medicine.create(db, obj_in=medicine_in)
    return medicine

from fastapi import Query

@router.get("/search", response_model=List[Medicine])
async def search_medicines(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search medicines by name.
    """
    from sqlalchemy import select
    from app.models.medicine import Medicine as MedicineModel
    
    # Search by name
    query = select(MedicineModel).filter(MedicineModel.name.ilike(f"%{q}%"))
    
    # Filter by hospital if user has a hospital_id (Doctor/Admin)
    if current_user.hospital_id:
        query = query.filter(MedicineModel.hospital_id == current_user.hospital_id)
        
    # Limit results
    query = query.limit(20)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/", response_model=List[Medicine])
async def read_medicines(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of medicines from inventory.
    
    - **Hospital filtering**: Returns only medicines from the user's hospital
    - **Super admin**: Can view all medicines across all hospitals
    - **Pagination**: Use skip/limit for pagination
    """
    # Filter by hospital if user has a hospital_id
    if current_user.hospital_id:
        from sqlalchemy import select
        from app.models.medicine import Medicine as MedicineModel
        query = select(MedicineModel).filter(MedicineModel.hospital_id == current_user.hospital_id).offset(skip).limit(limit)
        result = await db.execute(query)
        medicines = result.scalars().all()
        return medicines
    else:
        # Super admin without hospital can see all
        medicines = await crud_medicine.get_multi(db, skip=skip, limit=limit)
        return medicines

@router.patch("/{id}/add-stock", response_model=Medicine)
async def add_stock(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    quantity: int,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Add stock quantity to a medicine.
    
    - Increases the medicine quantity by the specified amount
    - Automatically logs the inventory change for audit purposes
    - Requires hospital admin authentication
    - Validates hospital access (can only modify your hospital's medicines)
    """
    medicine = await crud_medicine.get(db, id=id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    # Check hospital access
    if current_user.hospital_id and medicine.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    new_quantity = medicine.quantity + quantity
    medicine = await crud_medicine.update(db, db_obj=medicine, obj_in={"quantity": new_quantity})
    
    # Log it
    log_in = InventoryLogCreate(
        medicine_id=id,
        change_type=InventoryChangeType.ADDED,
        quantity_changed=quantity,
        reason="Stock added via API"
    )
    await crud_inventory_log.create(db, obj_in=log_in)
    
    return medicine

@router.patch("/{id}/remove-stock", response_model=Medicine)
async def remove_stock(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    quantity: int,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Remove stock quantity from a medicine.
    
    - Decreases the medicine quantity by the specified amount
    - Validates sufficient stock is available before removal
    - Automatically logs the inventory change for audit purposes
    - Requires hospital admin authentication
    - Validates hospital access (can only modify your hospital's medicines)
    """
    medicine = await crud_medicine.get(db, id=id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    # Check hospital access
    if current_user.hospital_id and medicine.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if medicine.quantity < quantity:
         raise HTTPException(status_code=400, detail="Not enough stock")

    new_quantity = medicine.quantity - quantity
    medicine = await crud_medicine.update(db, db_obj=medicine, obj_in={"quantity": new_quantity})
    
    # Log it
    log_in = InventoryLogCreate(
        medicine_id=id,
        change_type=InventoryChangeType.REMOVED,
        quantity_changed=quantity,
        reason="Stock removed via API"
    )
    await crud_inventory_log.create(db, obj_in=log_in)
    
    return medicine

@router.put("/{id}", response_model=Medicine)
async def update_medicine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    medicine_in: MedicineUpdate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Update medicine information.
    
    - Update name, description, price, or quantity
    - Requires hospital admin authentication
    - Can only update medicines from your hospital
    - Can only update records you created (unless super admin)
    """
    medicine = await crud_medicine.get(db, id=id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    if current_user.role != "super_admin" and medicine.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if current_user.role != "super_admin" and medicine.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="You do not own this record")
        
    medicine = await crud_medicine.update(db, db_obj=medicine, obj_in=medicine_in)
    return medicine

@router.delete("/{id}", response_model=Medicine)
async def delete_medicine(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Delete a medicine from inventory.
    
    - Permanently removes the medicine record
    - Requires hospital admin authentication
    - Can only delete medicines from your hospital
    - Can only delete records you created (unless super admin)
    """
    medicine = await crud_medicine.get(db, id=id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    if current_user.role != "super_admin" and medicine.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if current_user.role != "super_admin" and medicine.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="You do not own this record")
    medicine = await crud_medicine.remove(db, id=id)
    return medicine
