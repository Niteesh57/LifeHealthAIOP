from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.appointment import appointment as crud_appointment
from app.schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Appointment)
async def create_appointment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    appointment_in: AppointmentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new appointment.
    
    - Link patient to doctor
    - Set appointment date and time slot
    - Record severity and description
    - Add remarks (text, lab, medicine)
    - Optionally link to lab report
    """
    appointment = await crud_appointment.create(db, obj_in=appointment_in)
    return appointment

@router.get("/", response_model=List[Appointment])
async def read_appointments(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of appointments.
    
    - Returns all appointments
    - Can be filtered by patient or doctor
    - **Pagination**: Use skip/limit for pagination
    """
    appointments = await crud_appointment.get_multi(db, skip=skip, limit=limit)
    return appointments

@router.get("/{id}", response_model=Appointment)
async def read_appointment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get appointment details by ID.
    
    - Includes patient info, doctor, date, slot
    - Shows remarks and lab report links
    """
    appointment = await crud_appointment.get(db, id=id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{id}", response_model=Appointment)
async def update_appointment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    appointment_in: AppointmentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update appointment information.
    
    - Change date/time slot
    - Update severity or description
    - Modify remarks
    - Link to lab report
    - Set follow-up date
    """
    appointment = await crud_appointment.get(db, id=id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment = await crud_appointment.update(db, db_obj=appointment, obj_in=appointment_in)
    return appointment

@router.delete("/{id}", response_model=Appointment)
async def delete_appointment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancel/delete an appointment.
    
    - Permanently removes the appointment record
    """
    appointment = await crud_appointment.get(db, id=id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment = await crud_appointment.remove(db, id=id)
    return appointment
