from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db, get_current_user_id
from app.services.anniversary_service import AnniversaryService
from app.schemas.anniversary import AnniversaryCreate, AnniversaryUpdate

router = APIRouter()


@router.get("/templates")
def get_templates(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = AnniversaryService(db)
    templates = service.get_templates()
    return {"code": 0, "message": "success", "data": {"list": templates}}


@router.get("/")
def list_anniversaries(
    contact_id: str = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    anniversaries = service.get_anniversaries(user_id, contact_id)
    return {"code": 0, "message": "success", "data": {"list": anniversaries}}


@router.post("/")
def create_anniversary(
    data: AnniversaryCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    anniversary = service.create_anniversary(user_id, data)
    return {"code": 0, "message": "success", "data": anniversary}


@router.put("/{anniversary_id}")
def update_anniversary(
    anniversary_id: str,
    data: AnniversaryUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    try:
        anniversary = service.update_anniversary(user_id, anniversary_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": anniversary}


@router.delete("/{anniversary_id}")
def delete_anniversary(
    anniversary_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    try:
        service.delete_anniversary(user_id, anniversary_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": None}
