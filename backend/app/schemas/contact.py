from typing import Optional

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(..., max_length=20)
    relationship: str = Field(..., max_length=50)
    avatar: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=200)


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=20)
    relationship: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=200)


class ContactResponse(BaseModel):
    contact_id: str
    name: str
    avatar: Optional[str]
    relationship: str
    notes: Optional[str]
    anniversary_count: int
    created_at: str

    class Config:
        orm_mode = True
