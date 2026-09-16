import re
from typing import Optional

from pydantic import BaseModel, Field, validator


class SendSmsRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    type: str = Field(..., pattern="^(register|login|reset)$")

    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    sms_code: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=6, max_length=20)
    nickname: Optional[str] = Field(None, max_length=50)


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    password: Optional[str] = None
    sms_code: Optional[str] = None

    @validator("sms_code", always=True)
    def validate_login_method(cls, v, values):
        if not values.get("password") and not v:
            raise ValueError("密码和验证码至少填写一项")
        return v


class ChangePasswordRequest(BaseModel):
    old_password: Optional[str] = None
    sms_code: Optional[str] = None
    new_password: str = Field(..., min_length=6, max_length=20)


class AuthResponse(BaseModel):
    user_id: str
    token: str
    expires_in: int
