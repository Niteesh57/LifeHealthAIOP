from app.crud.base import CRUDBase
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

class CRUDAppointment(CRUDBase[Appointment, AppointmentCreate, AppointmentUpdate]):
    pass

appointment = CRUDAppointment(Appointment)
