from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user_memory import UserMemory
import logging

logger = logging.getLogger(__name__)

async def add_long_term_memory(user_id: str, content: str, db: AsyncSession):
    """Stores a piece of information in long-term memory."""
    try:
        memory = UserMemory(user_id=user_id, content=content)
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        logger.info(f"Stored memory for user {user_id}: {content}")
        return memory
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        return None

async def get_long_term_memories(user_id: str, db: AsyncSession, limit: int = 5):
    """Retrieves recent long-term memories."""
    try:
        # Get most recent memories
        query = select(UserMemory).filter(UserMemory.user_id == user_id).order_by(UserMemory.created_at.desc()).limit(limit)
        result = await db.execute(query)
        memories = result.scalars().all() 
        return [m.content for m in memories]
    except Exception as e:
        logger.error(f"Failed to fetch memories: {e}")
        return []
