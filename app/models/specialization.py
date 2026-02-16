import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Specialization(Base):
    __tablename__ = "specializations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
