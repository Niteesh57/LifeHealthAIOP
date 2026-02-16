from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.availability import availability as crud_availability
from app.schemas.availability import Availability, AvailabilityBulkCreate, AvailabilityCreate, AvailabilityUpdate
from app.models.user import User

router = APIRouter()

@router.get("/")
async def read_availability(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Returns count of doctors available on each day of the week from current hospital.
    """
    # Only show availability for doctors from current user's hospital
    if current_user.hospital_id:
        from sqlalchemy import select, func, distinct
        from app.models.availability import Availability as AvailabilityModel
        from app.models.doctor import Doctor
        
        # Get doctor IDs (primary key, not user_id) from current hospital
        doctor_query = select(Doctor.id).filter(Doctor.hospital_id == current_user.hospital_id)
        doctors_result = await db.execute(doctor_query)
        doctor_ids = [r[0] for r in doctors_result.all()]
        
        if doctor_ids:
            # Get all availability records for doctors in this hospital
            query = select(AvailabilityModel).filter(
                AvailabilityModel.staff_type == 'doctor',
                AvailabilityModel.staff_id.in_(doctor_ids)
            )
            result = await db.execute(query)
            availability_records = result.scalars().all()
            
            # Count unique doctors per day
            day_counts = {}
            for record in availability_records:
                day = record.day_of_week
                if day not in day_counts:
                    day_counts[day] = set()
                day_counts[day].add(record.staff_id)
            
            # Convert sets to counts
            return {day: len(doctors) for day, doctors in day_counts.items()}
        else:
            return {}
    else:
        # Super admin without hospital - show all doctors' availability
        from sqlalchemy import select
        from app.models.availability import Availability as AvailabilityModel
        
        # Get all doctor availability
        query = select(AvailabilityModel).filter(
            AvailabilityModel.staff_type == 'doctor'
        )
        result = await db.execute(query)
        availability_records = result.scalars().all()
        
        # Count unique doctors per day
        day_counts = {}
        for record in availability_records:
            day = record.day_of_week
            if day not in day_counts:
                day_counts[day] = set()
            day_counts[day].add(record.staff_id)
        
        # Convert sets to counts
        return {day: len(doctors) for day, doctors in day_counts.items()}

@router.put("/{id}", response_model=Availability)
async def update_availability(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    availability_in: AvailabilityUpdate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    availability = await crud_availability.get(db, id=id)
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")

    # Calculate new values effective for validation
    start_time = availability_in.start_time if availability_in.start_time is not None else availability.start_time
    end_time = availability_in.end_time if availability_in.end_time is not None else availability.end_time
    day_of_week = availability_in.day_of_week if availability_in.day_of_week is not None else availability.day_of_week

    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    if await crud_availability.check_overlap(
        db,
        staff_id=availability.staff_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        exclude_id=id
    ):
        raise HTTPException(status_code=400, detail="Time slot overlaps with an existing slot")

    return await crud_availability.update(db, db_obj=availability, obj_in=availability_in)

@router.delete("/{id}", response_model=Availability)
async def delete_availability(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    availability = await crud_availability.get(db, id=id)
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    return await crud_availability.remove(db, id=id)
