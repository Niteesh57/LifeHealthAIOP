from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate

class CRUDDoctor(CRUDBase[Doctor, DoctorCreate, DoctorUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[Doctor]:
        query = select(Doctor).options(selectinload(Doctor.user), selectinload(Doctor.hospital)).filter(Doctor.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Doctor]:
        query = select(Doctor).options(selectinload(Doctor.user), selectinload(Doctor.hospital)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

doctor = CRUDDoctor(Doctor)
