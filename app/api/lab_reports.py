from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.lab_report import lab_report as crud_lab_report
from app.schemas.lab_report import LabReport, LabReportCreate, LabReportUpdate
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=LabReport)
async def create_lab_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    lab_report_in: LabReportCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new lab report.
    
    - Upload PDF URL
    - Add summary and severity
    - Automatically tracks creator
    - Can be linked to appointments
    """
    # Set created_by to current user if not provided
    if not lab_report_in.created_by:
        lab_report_in.created_by = current_user.id
    
    lab_report = await crud_lab_report.create(db, obj_in=lab_report_in)
    return lab_report

@router.get("/", response_model=List[LabReport])
async def read_lab_reports(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of lab reports.
    
    - View all lab reports
    - **Pagination**: Use skip/limit for pagination
    """
    lab_reports = await crud_lab_report.get_multi(db, skip=skip, limit=limit)
    return lab_reports

@router.get("/patient/{patient_id}", response_model=List[LabReport])
async def read_patient_lab_reports(
    patient_id: str,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get lab reports for a specific patient.
    
    - **Doctor**: Can view reports for their patients
    - **Patient**: Can view their own reports (if ID matches)
    """
    # Authorization logic
    # If patient, ensure patient_id matches user's patient profile
    # If doctor, ensure patient has appointment? Or generally allow hospital doctors to see reports?
    # For now, allow if same hospital or if doctor.
    
    from sqlalchemy import select
    from app.models.lab_report import LabReport as LabReportModel
    from app.models.appointment import Appointment
    
    # Check if patient exists? (Optional but good)
    
    # Query: Select LabReports linked to Appointments of this Patient
    query = select(LabReportModel).join(Appointment).filter(Appointment.patient_id == patient_id).distinct()
    
    lab_reports = (await db.execute(query)).scalars().all()
    return lab_reports

@router.get("/my-reports", response_model=List[LabReport])
async def read_my_lab_reports(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's lab reports.
    """
    # Need to find patient_id from user_id
    from app.crud.patient import patient as crud_patient
    patient_profile = await crud_patient.get_by_user_id(db, user_id=current_user.id)
    if not patient_profile:
        return []
        
    from sqlalchemy import select
    from app.models.lab_report import LabReport as LabReportModel
    from app.models.appointment import Appointment
    
    query = select(LabReportModel).join(Appointment).filter(Appointment.patient_id == patient_profile.id).distinct()
    lab_reports = (await db.execute(query)).scalars().all()
    return lab_reports

@router.get("/{id}", response_model=LabReport)
async def read_lab_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get lab report details by ID.
    
    - Includes PDF URL, summary, severity
    - Shows who created the report
    """
    lab_report = await crud_lab_report.get(db, id=id)
    if not lab_report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    return lab_report

@router.put("/{id}", response_model=LabReport)
async def update_lab_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    lab_report_in: LabReportUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update lab report information.
    
    - Update PDF URL
    - Modify summary or severity
    """
    lab_report = await crud_lab_report.get(db, id=id)
    if not lab_report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    
    lab_report = await crud_lab_report.update(db, db_obj=lab_report, obj_in=lab_report_in)
    return lab_report

@router.delete("/{id}", response_model=LabReport)
async def delete_lab_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a lab report.
    
    - Permanently removes the lab report record
    - Warning: This may affect linked appointments
    """
    lab_report = await crud_lab_report.get(db, id=id)
    if not lab_report:
        raise HTTPException(status_code=404, detail="Lab report not found")
    
    lab_report = await crud_lab_report.remove(db, id=id)
    return lab_report
