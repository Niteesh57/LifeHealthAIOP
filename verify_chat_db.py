import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.appointment_chat import AppointmentChat
from app.models.user import User
from app.models.appointment import Appointment

async def verify_chat_table():
    async with SessionLocal() as session:
        print("Checking AppointmentChat table...")
        try:
            # Create a dummy chat entry
            # We need valid appointment_id and user_id. 
            # Ideally we should fetch existing ones or create dummy ones if not exists.
            # For simplicity, let's just try to query the table to see if it exists (select count)
            # If table doesn't exist, this will throw an error immediately.
            
            query = select(AppointmentChat).limit(1)
            result = await session.execute(query)
            print("Query executed successfully. Table exists.")
            
        except Exception as e:
            print(f"Error accessing table: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_chat_table())
