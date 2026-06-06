from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.note import NoteStatus

class NoteBase(BaseModel):
    title: str

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    file_type: str
    status: NoteStatus
    created_at: datetime
    
    model_config = {"from_attributes": True}
