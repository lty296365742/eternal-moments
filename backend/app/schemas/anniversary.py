from typing import Optional

from pydantic import BaseModel, Field


class AnniversaryCreate(BaseModel):
    contact_id: str
    title_key: Optional[str] = None
    title: Optional[str] = Field(None, max_length=30)
    date: str = Field(..., pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
    repeat_type: Optional[str] = Field(None, pattern="^(yearly|monthly|once)$")


class AnniversaryUpdate(BaseModel):
    title_key: Optional[str] = None
    title: Optional[str] = Field(None, max_length=30)
    date: Optional[str] = Field(None, pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
    repeat_type: Optional[str] = Field(None, pattern="^(yearly|monthly|once)$")
