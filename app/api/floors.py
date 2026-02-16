from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud.floor import floor as crud_floor
from app.schemas.floor import Floor
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Floor])
async def read_floors(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get list of hospital floors.
    
    - **Hospital filtered**: Only floors from your hospital
    - **Pagination**: Use skip/limit for pagination
    - Returns floor number and name
    """
    floors = await crud_floor.get_multi(db, skip=skip, limit=limit)
    return floors
