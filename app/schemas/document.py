from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    file_url: str
    file_type: Optional[str] = None
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
