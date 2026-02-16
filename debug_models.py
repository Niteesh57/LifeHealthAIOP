from sqlalchemy import create_engine
from app.core.database import Base
from app.models.user import User
from app.models.hospital import Hospital
from app.models.doctor import Doctor
from app.models.nurse import Nurse
from app.models.patient import Patient
from app.models.medicine import Medicine, InventoryLog
from app.models.lab_test import LabTest
from app.models.floor import Floor
from app.models.availability import Availability
from sqlalchemy.orm import configure_mappers

try:
    configure_mappers()
    print("Mappers configured successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
