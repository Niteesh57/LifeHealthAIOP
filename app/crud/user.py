from typing import Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        from app.utils.id_generator import generate_compact_id
        from app.models.user import UserRole
        
        # Determine prefix based on role
        prefix = "USR"
        if obj_in.role == UserRole.DOCTOR:
            prefix = "DOC"
        elif obj_in.role == UserRole.NURSE:
            prefix = "NUR"
        elif obj_in.role == UserRole.PATIENT:
            prefix = "PAT"
        elif obj_in.role == UserRole.HOSPITAL_ADMIN:
            prefix = "HAP"
        elif obj_in.role == UserRole.SUPER_ADMIN:
            prefix = "SAD"
            
        compact_id = generate_compact_id(prefix)
        
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role=obj_in.role.value,
            is_active=obj_in.is_active,
            is_verified=obj_in.is_verified,
            hospital_id=obj_in.hospital_id,
            compact_id=compact_id,
            image=obj_in.image
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

user = CRUDUser(User)
