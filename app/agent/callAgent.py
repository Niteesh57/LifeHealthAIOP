import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    RoomInputOptions,
)
from livekit.plugins import google
from app.agent.Tools.CallTools import book_appointment, check_availability

load_dotenv()
logger = logging.getLogger("receptionist-agent")


class ReceptionistAgent(Agent):
    def __init__(self, instructions: str):
        super().__init__(
            instructions=instructions,
            tools=[book_appointment, check_availability],
        )


async def entrypoint(ctx: JobContext):
    logger.info("Starting Receptionist Agent")

    await ctx.connect()
    
    # Extract appointment_id from metadata
    appointment_id = None
    if ctx.job.metadata:
        import json
        try:
            metadata = json.loads(ctx.job.metadata)
            appointment_id = metadata.get("appointment_id")
        except:
            logger.warning("Failed to parse metadata JSON")
            
    # Default context
    doctor_name = "your doctor"
    medications = "your prescribed medications"
    patient_name = "there"
    
    # Fetch details if appointment_id is present
    if appointment_id:
        from app.core.database import SessionLocal
        from app.crud.appointment import appointment as crud_appointment
        from sqlalchemy import select
        from app.models.appointment import Appointment
        from app.models.doctor import Doctor
        from app.models.user import User
        from sqlalchemy.orm import selectinload

        async with SessionLocal() as db:
            # We need a custom query to get doctor name and remarks
            query = select(Appointment).options(
                selectinload(Appointment.doctor).selectinload(Doctor.user),
                selectinload(Appointment.patient)
            ).filter(Appointment.id == appointment_id)
            
            result = await db.execute(query)
            appointment = result.scalars().first()
            
            if appointment:
                if appointment.doctor and appointment.doctor.user:
                    doctor_name = f"Dr. {appointment.doctor.user.full_name}"
                
                if appointment.patient:
                    patient_name = appointment.patient.full_name
                    
                # Extract medications from remarks
                # Remarks structure: { "medicine": [{"name": "...", "dosage": "..."}] }
                if appointment.remarks and isinstance(appointment.remarks, dict):
                    meds_list = appointment.remarks.get("medicine", [])
                    if meds_list:
                        # Format list of meds for speech
                        med_names = [m.get("name", "medicine") for m in meds_list]
                        medications = ", ".join(med_names)

    instructions = (
        f"You are a helpful medical assistant calling on behalf of {doctor_name} from LifeHealth Hospital. "
        f"You are speaking with {patient_name} (Patient ID: {appointment.patient_id if appointment else 'Unknown'}). "
        f"Ask them if the following medications are working fine: {medications}. "
        "Ask if they are facing any difficulties. "
        "If they say everything is fine, say thanks and goodbye. "
        "If they report issues, suggest booking a follow-up appointment with the doctor. "
        "Use the check_availability tool to find a slot, then book_appointment if they agree. "
        "IMPORTANT: Pass the Patient ID provided above to the book_appointment tool."
    )

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            instructions=instructions
        )
    )

    await session.start(
        agent=ReceptionistAgent(instructions=instructions),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            close_on_disconnect=True
        )
    )

    await session.generate_reply()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="receptionist-agent",
        )
    )