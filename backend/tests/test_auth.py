import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User

client = TestClient(app)

TEST_PHONE = "13900000001"
TEST_PASSWORD = "testpass123"


def cleanup_test_users():
    db = SessionLocal()
    try:
        db.query(User).filter(User.phone.like("139000000%")).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_test_data():
    cleanup_test_users()
    yield
    cleanup_test_users()


def test_send_sms_success():
    resp = client.post("/api/v1/auth/sms/send", json={"phone": TEST_PHONE, "type": "register"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0


def test_register_success():
    resp = client.post("/api/v1/auth/register", json={
        "phone": TEST_PHONE,
        "sms_code": "123456",
        "password": TEST_PASSWORD,
        "nickname": "测试用户",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["user_id"].startswith("U")
    assert data["token"]
    assert data["expires_in"] == 30 * 86400


def test_register_duplicate_phone():
    payload = {"phone": TEST_PHONE, "sms_code": "123456", "password": TEST_PASSWORD}
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 200
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 400


def test_register_wrong_sms_code():
    resp = client.post("/api/v1/auth/register", json={
        "phone": TEST_PHONE,
        "sms_code": "000000",
        "password": TEST_PASSWORD,
    })
    assert resp.status_code == 400


def test_login_with_password():
    client.post("/api/v1/auth/register", json={
        "phone": TEST_PHONE,
        "sms_code": "123456",
        "password": TEST_PASSWORD,
    })
    resp = client.post("/api/v1/auth/login", json={
        "phone": TEST_PHONE,
        "password": TEST_PASSWORD,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["token"]


def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={
        "phone": TEST_PHONE,
        "sms_code": "123456",
        "password": TEST_PASSWORD,
    })
    resp = client.post("/api/v1/auth/login", json={
        "phone": TEST_PHONE,
        "password": "wrongpass",
    })
    assert resp.status_code == 400


def test_login_with_sms_code():
    client.post("/api/v1/auth/register", json={
        "phone": TEST_PHONE,
        "sms_code": "123456",
        "password": TEST_PASSWORD,
    })
    resp = client.post("/api/v1/auth/login", json={
        "phone": TEST_PHONE,
        "sms_code": "123456",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == 0


def test_login_nonexistent_phone():
    resp = client.post("/api/v1/auth/login", json={
        "phone": "13900000099",
        "password": TEST_PASSWORD,
    })
    assert resp.status_code == 400
