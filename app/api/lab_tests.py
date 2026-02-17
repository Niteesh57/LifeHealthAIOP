from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.lab_test import lab_test as crud_lab_test
from app.schemas.lab_test import LabTest, LabTestUpdate
from app.models.user import User

router = APIRouter()

from fastapi import Query

@router.get("/search", response_model=List[LabTest])
async def search_lab_tests(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search lab tests by name.
    """
    from sqlalchemy import select
    from app.models.lab_test import LabTest as LabTestModel
    
    query = select(LabTestModel).filter(LabTestModel.name.ilike(f"%{q}%"))
    
    if current_user.hospital_id:
        query = query.filter(LabTestModel.hospital_id == current_user.hospital_id)
        
    query = query.limit(20)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/", response_model=List[LabTest])
async def read_lab_tests(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of lab tests available at the hospital.
    
    - **Hospital filtering**: Returns only lab tests from the user's hospital
    - **Super admin**: Can view lab tests from all hospitals
    - **Pagination**: Use skip/limit for pagination
    """
    # Filter by hospital if user has a hospital_id
    if current_user.hospital_id:
        from sqlalchemy import select
        from app.models.lab_test import LabTest as LabTestModel
        query = select(LabTestModel).filter(LabTestModel.hospital_id == current_user.hospital_id).offset(skip).limit(limit)
        result = await db.execute(query)
        lab_tests = result.scalars().all()
        return lab_tests
    else:
        # Super admin without hospital can see all
        lab_tests = await crud_lab_test.get_multi(db, skip=skip, limit=limit)
        return lab_tests

@router.put("/{id}", response_model=LabTest)
async def update_lab_test(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    lab_test_in: LabTestUpdate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Update lab test information.
    
    - Update name, description, price, or availability
    - Requires hospital admin authentication
    - Can only update lab tests from your hospital
    - Can only update records you created (unless super admin)
    """
    lab_test = await crud_lab_test.get(db, id=id)
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab Test not found")
    if current_user.role != "super_admin" and lab_test.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if current_user.role != "super_admin" and lab_test.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="You do not own this record")
        
    lab_test = await crud_lab_test.update(db, db_obj=lab_test, obj_in=lab_test_in)
    return lab_test

@router.delete("/{id}", response_model=LabTest)
async def delete_lab_test(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Delete a lab test.
    
    - Permanently removes the lab test record
    - Requires hospital admin authentication
    - Can only delete lab tests from your hospital
    - Can only delete records you created (unless super admin)
    """
    lab_test = await crud_lab_test.get(db, id=id)
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab Test not found")
    if current_user.role != "super_admin" and lab_test.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    if current_user.role != "super_admin" and lab_test.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="You do not own this record")
    lab_test = await crud_lab_test.remove(db, id=id)
    return lab_test
