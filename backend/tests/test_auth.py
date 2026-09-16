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


def _register_and_get_token(phone="13900000010", password="oldpass123"):
    resp = client.post("/api/v1/auth/register", json={
        "phone": phone,
        "sms_code": "123456",
        "password": password,
    })
    assert resp.status_code == 200
    return resp.json()["data"]["token"]


def test_get_me_success():
    client.post("/api/v1/auth/register", json={
        "phone": TEST_PHONE,
        "sms_code": "123456",
        "password": TEST_PASSWORD,
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "phone": TEST_PHONE,
        "password": TEST_PASSWORD,
    })
    token = login_resp.json()["data"]["token"]
    user_id = login_resp.json()["data"]["user_id"]

    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["user_id"] == user_id
    assert body["data"]["phone"] == TEST_PHONE


def test_get_me_without_token():
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 403


def test_change_password_with_old_password():
    token = _register_and_get_token()
    resp = client.put("/api/v1/auth/password", json={
        "old_password": "oldpass123",
        "new_password": "newpass456",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["code"] == 0

    # 新密码可登录，证明修改生效
    login_resp = client.post("/api/v1/auth/login", json={
        "phone": "13900000010",
        "password": "newpass456",
    })
    assert login_resp.status_code == 200


def test_change_password_wrong_old_password():
    token = _register_and_get_token()
    resp = client.put("/api/v1/auth/password", json={
        "old_password": "wrongpass",
        "new_password": "newpass456",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400


def test_change_password_unauthorized():
    resp = client.put("/api/v1/auth/password", json={
        "old_password": "oldpass123",
        "new_password": "newpass456",
    })
    assert resp.status_code == 403
