import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.contact import Contact

client = TestClient(app)

TEST_PHONE = "13900000101"
TEST_PASSWORD = "testpass123"


def cleanup_test_data():
    db = SessionLocal()
    try:
        test_users = db.query(User).filter(User.phone.like("139000001%")).all()
        for u in test_users:
            db.query(Contact).filter(Contact.user_id == u.user_id).delete(synchronize_session=False)
            db.delete(u)
        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_test_data():
    cleanup_test_data()
    yield
    cleanup_test_data()


@pytest.fixture
def auth_headers():
    resp = client.post("/api/v1/auth/register", json={
        "phone": TEST_PHONE,
        "sms_code": "123456",
        "password": TEST_PASSWORD,
        "nickname": "联系人测试用户",
    })
    assert resp.status_code == 200
    token = resp.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def _create_contact(headers, name="测试妈妈", relationship="母亲", notes="喜欢花"):
    return client.post("/api/v1/contacts/", json={
        "name": name,
        "relationship": relationship,
        "notes": notes,
    }, headers=headers)


def test_create_contact(auth_headers):
    resp = _create_contact(auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["contact_id"].startswith("C")
    assert data["name"] == "测试妈妈"
    assert data["relationship"] == "母亲"
    assert data["notes"] == "喜欢花"


def test_list_contacts(auth_headers):
    create_resp = _create_contact(auth_headers)
    contact_id = create_resp.json()["data"]["contact_id"]

    resp = client.get("/api/v1/contacts/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 1
    ids = [item["contact_id"] for item in data["list"]]
    assert contact_id in ids
    for item in data["list"]:
        assert item["anniversary_count"] == 0


def test_list_contacts_keyword(auth_headers):
    _create_contact(auth_headers, name="测试妈妈")

    resp = client.get("/api/v1/contacts/", params={"keyword": "测试"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 1

    resp = client.get("/api/v1/contacts/", params={"keyword": "不存在"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["list"] == []


def test_get_contact(auth_headers):
    create_resp = _create_contact(auth_headers)
    created = create_resp.json()["data"]

    resp = client.get(f"/api/v1/contacts/{created['contact_id']}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["contact_id"] == created["contact_id"]
    assert data["name"] == created["name"]

    resp = client.get("/api/v1/contacts/CXXXXXXXX", headers=auth_headers)
    assert resp.status_code == 404


def test_update_contact(auth_headers):
    create_resp = _create_contact(auth_headers)
    contact_id = create_resp.json()["data"]["contact_id"]

    resp = client.put(f"/api/v1/contacts/{contact_id}", json={"name": "新名字"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "新名字"


def test_get_relationships(auth_headers):
    resp = client.get("/api/v1/contacts/relationships", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["preset"]) == 10
    labels = [item["label"] for item in data["preset"]]
    assert "父亲" in labels
    assert "母亲" in labels
    assert data["custom"] == []

    # 创建自定义关系后，应出现在 custom 中
    _create_contact(auth_headers, name="自定义朋友", relationship="自定义关系X")
    resp = client.get("/api/v1/contacts/relationships", headers=auth_headers)
    data = resp.json()["data"]
    custom_labels = [item["label"] for item in data["custom"]]
    assert "自定义关系X" in custom_labels


def test_upload_avatar(auth_headers):
    # 最小合法 PNG（1x1 像素）
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    resp = client.post(
        "/api/v1/contacts/upload/avatar",
        files={"file": ("avatar.png", io.BytesIO(png_bytes), "image/png")},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["url"].startswith("/uploads/avatars/")

    # 上传的文件可通过静态路由访问
    file_resp = client.get(data["url"])
    assert file_resp.status_code == 200


def test_delete_contact(auth_headers):
    create_resp = _create_contact(auth_headers)
    contact_id = create_resp.json()["data"]["contact_id"]

    resp = client.delete(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["code"] == 0

    resp = client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_unauthorized():
    resp = client.get("/api/v1/contacts/")
    assert resp.status_code == 403
