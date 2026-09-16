import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db, get_current_user_id
from app.services.reminder_service import ReminderService

router = APIRouter()


@router.get("/")
def list_reminders(
    type: str = None,
    status: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ReminderService(db)
    total, reminders = service.get_reminders(user_id, type, status, page, page_size)
    return {
        "code": 0,
        "message": "success",
        "data": {"total": total, "list": reminders}
    }


@router.put("/{reminder_id}/read")
def mark_read(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ReminderService(db)
    try:
        service.mark_read(user_id, reminder_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": None}


@router.post("/{reminder_id}/blessing")
def regenerate_blessing(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ReminderService(db)
    try:
        blessing = service.regenerate_blessing(user_id, reminder_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="AI 服务暂不可用，请稍后重试")
    return {"code": 0, "message": "success", "data": {"blessing": blessing}}


@router.post("/{reminder_id}/gifts")
def regenerate_gifts(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ReminderService(db)
    try:
        gifts = service.regenerate_gifts(user_id, reminder_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="AI 服务暂不可用，请稍后重试")
    return {"code": 0, "message": "success", "data": {"gifts": gifts}}
