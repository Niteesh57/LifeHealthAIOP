from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.api import deps
from app.models.doctor import Doctor
from app.models.nurse import Nurse
from app.models.medicine import Medicine
from app.models.lab_test import LabTest
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.search import UnifiedSearchResult

router = APIRouter()

@router.get("/resources", response_model=UnifiedSearchResult)
async def search_resources(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search ONLY for Medicines and Lab Tests.
    """
    search_term = f"%{q}%"
    
    # 1. Search Medicines (by name, code, description)
    medicine_query = select(Medicine).filter(
        or_(
            Medicine.name.ilike(search_term),
            Medicine.unique_code.ilike(search_term),
            Medicine.description.ilike(search_term)
        )
    )
    medicines = (await db.execute(medicine_query)).scalars().all()
    
    # 2. Search Lab Tests (by name, description)
    lab_test_query = select(LabTest).filter(
        or_(
            LabTest.name.ilike(search_term),
            LabTest.description.ilike(search_term)
        )
    )
    lab_tests = (await db.execute(lab_test_query)).scalars().all()

    return {
        "doctors": [],
        "nurses": [],
        "medicines": medicines,
        "lab_tests": lab_tests,
        "users": []
    }

@router.get("/users-for-staff", response_model=List[UserSchema])
async def search_users_for_staff(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Search users to promote to staff.
    Excludes SUPER_ADMIN and HOSPITAL_ADMIN.
    Includes BASE, PATIENT, etc.
    """
    from app.models.user import UserRole
    search_term = f"%{q}%"
    
    user_query = select(User).filter(
        or_(
            User.full_name.ilike(search_term),
            User.email.ilike(search_term),
            User.compact_id.ilike(search_term)
        )
    ).filter(
        User.role.notin_([UserRole.SUPER_ADMIN.value, UserRole.HOSPITAL_ADMIN.value])
    ).limit(20)
    
    users = (await db.execute(user_query)).scalars().all()
    # Return minimal user info or full user object depending on needs. 
    # For now returning list of users which matches Schema if Any or User response schema.
    return users

@router.get("/patients", response_model=List[UserSchema])
async def search_patients(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search for patients (BASE or PATIENT role users).
    
    - Search by name or email
    - Returns only users with BASE or PATIENT role
    - Useful for appointment creation
    """
    from app.models.user import UserRole
    search_term = f"%{q}%"
    
    user_query = select(User).filter(
        or_(
            User.full_name.ilike(search_term),
            User.email.ilike(search_term)
        )
    ).filter(
        User.role.in_([UserRole.BASE.value, UserRole.PATIENT.value])
    ).limit(20)
    
    users = (await db.execute(user_query)).scalars().all()
    return users
