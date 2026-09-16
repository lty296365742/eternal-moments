import os
import uuid as uuid_lib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db, get_current_user_id
from app.services.contact_service import ContactService
from app.schemas.contact import ContactCreate, ContactUpdate

router = APIRouter()


@router.get("/relationships")
def get_relationships(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = ContactService(db)
    return {"code": 0, "message": "success", "data": service.get_relationships(user_id)}


@router.get("/")
def list_contacts(
    relationship: str = None,
    keyword: str = None,
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    total, contacts = service.get_contacts(user_id, relationship, keyword, page, page_size)
    return {
        "code": 0,
        "message": "success",
        "data": {"total": total, "list": contacts}
    }


@router.post("/")
def create_contact(
    data: ContactCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    contact = service.create_contact(user_id, data)
    return {"code": 0, "message": "success", "data": contact}


@router.get("/{contact_id}")
def get_contact(
    contact_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    try:
        contact = service.get_contact(user_id, contact_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": contact}


@router.put("/{contact_id}")
def update_contact(
    contact_id: str,
    data: ContactUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    try:
        contact = service.update_contact(user_id, contact_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": contact}


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    try:
        service.delete_contact(user_id, contact_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": None}


# 头像上传接口
@router.post("/upload/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{user_id}_{uuid_lib.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    url = f"/uploads/avatars/{filename}"
    return {"code": 0, "message": "success", "data": {"url": url}}
