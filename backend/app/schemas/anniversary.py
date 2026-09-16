from typing import Optional

from pydantic import BaseModel, Field, validator


def _validate_calendar_date(v):
    if v is None:
        return v
    month, day = map(int, v.split("-"))
    days_in_month = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
                     7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    if day > days_in_month[month]:
        raise ValueError("无效的日期")
    return v


class AnniversaryCreate(BaseModel):
    contact_id: str
    title_key: Optional[str] = None
    title: Optional[str] = Field(None, max_length=30)
    date: str = Field(..., pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
    repeat_type: Optional[str] = Field(None, pattern="^(yearly|monthly|once)$")

    @validator("date")
    def validate_calendar_date(cls, v):
        return _validate_calendar_date(v)


class AnniversaryUpdate(BaseModel):
    title_key: Optional[str] = None
    title: Optional[str] = Field(None, max_length=30)
    date: Optional[str] = Field(None, pattern=r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
    repeat_type: Optional[str] = Field(None, pattern="^(yearly|monthly|once)$")

    @validator("date")
    def validate_calendar_date(cls, v):
        return _validate_calendar_date(v)
