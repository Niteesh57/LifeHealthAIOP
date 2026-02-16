from app.crud.base import CRUDBase
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalCreate, HospitalUpdate

class CRUDHospital(CRUDBase[Hospital, HospitalCreate, HospitalUpdate]):
    pass

hospital = CRUDHospital(Hospital)
