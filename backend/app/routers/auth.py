from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.services.auth_service import AuthService
from app.schemas.auth import (
    SendSmsRequest, RegisterRequest, LoginRequest,
    ChangePasswordRequest, AuthResponse
)
from app.core.config import settings

router = APIRouter()


@router.post("/sms/send")
def send_sms(data: SendSmsRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    success = service.send_sms_code(data.phone, data.type)
    if not success:
        raise HTTPException(status_code=500, detail="发送失败")
    return {"code": 0, "message": "success", "data": None}


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"user_id": user.user_id, "phone": user.phone})
    return {
        "code": 0,
        "message": "success",
        "data": AuthResponse(
            user_id=user.user_id,
            token=token,
            expires_in=settings.JWT_EXPIRE_DAYS * 86400
        )
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"user_id": user.user_id, "phone": user.phone})
    return {
        "code": 0,
        "message": "success",
        "data": AuthResponse(
            user_id=user.user_id,
            token=token,
            expires_in=settings.JWT_EXPIRE_DAYS * 86400
        )
    }
