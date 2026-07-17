from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List

class NoteBase(BaseModel):
    title: str = Field(..., max_length=200, description="The title of the note")
    body: str = Field(..., description="The content of the note")
    tags: List[str] = Field(default_factory=list, description="A list of tags associated with the note")

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    body: str | None = None
    tags: List[str] | None = None

class NoteInDB(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Note(NoteInDB):
    pass
