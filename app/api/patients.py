from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.patient import patient as crud_patient
from app.schemas.patient import Patient, PatientUpdate, PatientCreate
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Patient)
async def create_patient(
    *,
    db: AsyncSession = Depends(deps.get_db),
    patient_in: PatientCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new patient record.
    
    - Automatically creates a user account for the patient
    - Requires email for user account creation
    - Sets default password: "Patient@123"
    - Assigns PATIENT role and hospital_id
    - Captures patient demographic information
    - Can optionally assign a doctor to the patient
    """
    from app.crud.user import user as crud_user
    from app.schemas.user import UserCreate
    from app.core.security import get_password_hash
    from app.models.user import UserRole
    
    # Assign hospital_id if user has one
    if current_user.hospital_id and not patient_in.hospital_id:
        patient_in.hospital_id = current_user.hospital_id
    
    # Check if user with this email already exists
    existing_user = await crud_user.get_by_email(db, email=patient_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Auto-create user account for patient
    user_data = UserCreate(
        email=patient_in.email,
        full_name=patient_in.full_name,
        phone_number=patient_in.phone,
        password=get_password_hash(patient_in.password or "Patient@123"),
        role=UserRole.PATIENT,
        hospital_id=patient_in.hospital_id,
        is_active=True,
        is_verified=True
    )
    created_user = await crud_user.create(db, obj_in=user_data)
    
    # Create patient record linked to user
    patient_data = patient_in.model_dump(exclude={"email", "password"})
    patient_data["user_id"] = created_user.id
    
    from app.models.patient import Patient as PatientModel
    patient = PatientModel(**patient_data)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    
    return patient

@router.put("/{id}", response_model=Patient)
async def update_patient(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    patient_in: PatientUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update patient information.
    
    - Modify patient demographics
    - Reassign doctor
    """
    patient = await crud_patient.get(db, id=id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = await crud_patient.update(db, db_obj=patient, obj_in=patient_in)
    return patient

@router.delete("/{id}", response_model=Patient)
async def delete_patient(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a patient record.
    
    - Permanently removes patient
    """
    patient = await crud_patient.get(db, id=id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = await crud_patient.remove(db, id=id)
    return patient

@router.get("/", response_model=List[Patient])
async def read_patients(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve patients.
    
    - **Hospital filtered**: Only shows patients from your hospital
    - **Pagination**: Use skip/limit for pagination
    """
    patients = await crud_patient.get_multi(db, skip=skip, limit=limit)
    return patients
