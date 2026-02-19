from livekit.agents import function_tool, RunContext
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

@function_tool
async def check_availability(
    context: RunContext,
    doctor_name: str,
    date_str: str,
):
    """Check availability for a doctor on a specific date.
    
    Args:
        doctor_name: Name of the doctor (e.g. "Dr. Smith" or just "Smith").
        date_str: Date to check in YYYY-MM-DD format (e.g. "2023-10-27").
    """
    logger.info(f"Checking availability for {doctor_name} on {date_str}")
    
    try:
        from app.core.database import SessionLocal
        from app.models.doctor import Doctor
        from app.models.user import User
        from sqlalchemy import select
        from app.agent.Tools.doctorTools import get_doctors_with_availability
        
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        async with SessionLocal() as db:
            # 1. Find doctor by name
            query = select(Doctor).join(User, Doctor.user_id == User.id).filter(User.full_name.ilike(f"%{doctor_name}%"))
            result = await db.execute(query)
            doctor = result.scalars().first()
            
            if not doctor:
                return f"I couldn't find a doctor named {doctor_name}."
            
            # 2. Get availability
            # Reuse doctorTools logic or simplify
            # We need the hospital_id, let's assume filtering by the doctor's hospital
            availability_data = await get_doctors_with_availability(doctor.hospital_id, db, target_date)
            
            # Filter for specific doctor
            doc_avail = next((d for d in availability_data if d["doctor_id"] == doctor.id), None)
            
            if not doc_avail or not doc_avail["available_slots"]:
                return f"Dr. {doctor_name} has no available slots on {date_str}."
            
            slots = ", ".join(doc_avail["available_slots"][:5]) # List first 5
            return f"Dr. {doctor_name} is available at: {slots}."
            
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return "I'm having trouble checking the schedule right now."

@function_tool
async def book_appointment(
    context: RunContext,
    doctor_name: str,
    appointment_time: str,
    patient_id: str, # Agent must provide this from context
):
    """Book an appointment with a doctor. USE THIS ONLY after confirming the time with the user.
    
    Args:
        doctor_name: Name of the doctor.
        appointment_time: Date and time in YYYY-MM-DD HH:MM format (e.g. "2023-10-27 10:30").
        patient_id: The ID of the patient (from your instructions).
    """
    logger.info(f"Booking appointment with {doctor_name} at {appointment_time} for patient {patient_id}")
    
    try:
        from app.core.database import SessionLocal
        from app.models.doctor import Doctor
        from app.models.user import User
        from app.models.appointment import Appointment, AppointmentStatus
        from sqlalchemy import select
        from datetime import datetime
        
        dt = datetime.strptime(appointment_time, "%Y-%m-%d %H:%M")
        appt_date = dt.date()
        slot = dt.strftime("%H:%M")
        
        async with SessionLocal() as db:
            doc_query = select(Doctor).join(User, Doctor.user_id == User.id).filter(User.full_name.ilike(f"%{doctor_name}%"))
            doc_res = await db.execute(doc_query)
            doctor = doc_res.scalars().first()
            
            if not doctor:
                return f"Error: Doctor {doctor_name} not found."

            new_appt = Appointment(
                patient_id=patient_id,
                doctor_id=doctor.id,
                date=appt_date,
                slot=slot,
                status=AppointmentStatus.STARTED.value,
                description="AI Follow-up Booking",
                severity="low"
            )
            db.add(new_appt)
            await db.commit()
            
            return f"Booked appointment with Dr. {doctor_name} on {appt_date} at {slot}."

    except Exception as e:
        logger.error(f"Booking failed: {e}")
        return "Failed to book appointment due to technical error."
