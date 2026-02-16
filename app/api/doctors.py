from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.api import deps
from app.crud.doctor import doctor as crud_doctor
from app.schemas.doctor import DoctorResponse, DoctorUpdate
from app.models.user import User
from app.models.doctor import Doctor

router = APIRouter()

@router.get("/search-potential", response_model=List[Any])
async def search_potential_doctors(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Search for potential doctors to add.
    
    - **Admin only**
    - Searches users with DOCTOR role not yet added to hospital
    """
    from app.models.user import UserRole
    search_term = f"%{q}%"
    
    query = select(User).filter(
        or_(
            User.full_name.ilike(search_term),
            User.email.ilike(search_term)
        )
    ).filter(User.role == UserRole.DOCTOR.value).limit(20)
    
    users = (await db.execute(query)).scalars().all()
    return users

@router.get("/search", response_model=List[DoctorResponse])
async def search_doctors(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search doctors in your hospital.
    
    - Search by name or specialization
    - Returns doctors from your hospital only
    """
    doctors = await crud_doctor.search(db, query=q, hospital_id=current_user.hospital_id)
    return doctors

@router.get("/", response_model=List[DoctorResponse])
async def read_doctors(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of doctors.
    
    - **Hospital filtered**: Only from your hospital
    - **Pagination**: Use skip/limit
    """
    doctors = await crud_doctor.get_multi(db, skip=skip, limit=limit)
    return doctors

@router.put("/{id}", response_model=DoctorResponse)
async def update_doctor(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    doctor_in: DoctorUpdate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Update doctor information.
    
    - **Admin only**
    - Modify specialization, availability, etc.
    """
    doctor = await crud_doctor.get(db, id=id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor = await crud_doctor.update(db, db_obj=doctor, obj_in=doctor_in)
    return doctor

@router.delete("/{id}", response_model=DoctorResponse)
async def delete_doctor(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Remove doctor from hospital.
    
    - **Admin only**
    - Removes doctor record
    """
    doctor = await crud_doctor.get(db, id=id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor = await crud_doctor.remove(db, id=id)
    return doctor
