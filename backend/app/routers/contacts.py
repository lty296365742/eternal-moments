import os
import uuid as uuid_lib

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
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
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
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
ALLOWED_AVATAR_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/upload/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    if ext not in ALLOWED_AVATAR_EXTS:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/webp 格式的图片")

    content = file.file.read(MAX_AVATAR_SIZE + 1)
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")

    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{user_id}_{uuid_lib.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/uploads/avatars/{filename}"
    return {"code": 0, "message": "success", "data": {"url": url}}
