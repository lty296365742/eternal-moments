from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, get_current_user_id
from app.services.holiday_service import HolidayService
from app.schemas.holiday import ToggleRemindRequest

router = APIRouter()


@router.get("/")
def list_holidays(
    relationship: str = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = HolidayService(db)
    holidays = service.get_holidays(relationship)
    return {"code": 0, "message": "success", "data": {"list": [service.serialize_holiday(h) for h in holidays]}}


@router.put("/contacts/{contact_id}/holidays/{holiday_id}/remind")
def set_remind(
    contact_id: str,
    holiday_id: str,
    data: ToggleRemindRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = HolidayService(db)
    service.set_remind_enabled(user_id, contact_id, holiday_id, data.remind_enabled)
    return {"code": 0, "message": "success", "data": None}
