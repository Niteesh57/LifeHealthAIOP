from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AppointmentChat(Base):
    __tablename__ = "appointment_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(String, ForeignKey("appointments.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    message = Column(Text, nullable=False) # User question
    response = Column(Text, nullable=True) # AI answer
    document_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    # appointment = relationship("Appointment", back_populates="chats")
    # user = relationship("User", back_populates="chats")

# Pydantic Schemas for API
class ChatBase(BaseModel):
    message: str
    response: str | None = None
    document_url: str | None = None

class ChatCreate(ChatBase):
    appointment_id: str
    user_id: str

class ChatResponse(ChatBase):
    id: int
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
