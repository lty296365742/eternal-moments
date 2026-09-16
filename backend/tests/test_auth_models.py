import pytest
from pydantic import ValidationError

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.schemas.auth import LoginRequest, SendSmsRequest


class TestPasswordHashing:
    def test_hash_and_verify_roundtrip(self):
        hashed = get_password_hash("secret123")
        assert hashed != "secret123"
        assert verify_password("secret123", hashed) is True

    def test_verify_rejects_wrong_password(self):
        hashed = get_password_hash("secret123")
        assert verify_password("wrongpass", hashed) is False


class TestJwt:
    def test_create_decode_roundtrip(self):
        payload = {"user_id": "abc123", "phone": "13800138000"}
        token = create_access_token(payload)
        decoded = decode_access_token(token)
        assert decoded["user_id"] == "abc123"
        assert decoded["phone"] == "13800138000"
        assert "exp" in decoded


class TestSendSmsRequest:
    def test_accepts_valid_phone(self):
        req = SendSmsRequest(phone="13800138000", type="register")
        assert req.phone == "13800138000"

    def test_rejects_invalid_phone(self):
        with pytest.raises(ValidationError):
            SendSmsRequest(phone="12345678901", type="register")


class TestLoginRequest:
    def test_rejects_when_neither_password_nor_sms_code(self):
        with pytest.raises(ValidationError):
            LoginRequest(phone="13800138000")

    def test_accepts_password_only(self):
        req = LoginRequest(phone="13800138000", password="secret123")
        assert req.password == "secret123"

    def test_accepts_sms_code_only(self):
        req = LoginRequest(phone="13800138000", sms_code="123456")
        assert req.sms_code == "123456"
