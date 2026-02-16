from app.crud.base import CRUDBase
from app.models.availability import Availability
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate

class CRUDAvailability(CRUDBase[Availability, AvailabilityCreate, AvailabilityUpdate]):
    pass

availability = CRUDAvailability(Availability)
