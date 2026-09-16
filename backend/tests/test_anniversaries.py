import re
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.contact import Contact
from app.models.anniversary import Anniversary
from app.models.holiday import ContactHoliday

client = TestClient(app)

TEST_PHONE = "13900000201"
TEST_PASSWORD = "testpass123"
TEST_PHONE_2 = "13900000301"


def cleanup_test_data():
    db = SessionLocal()
    try:
        test_users = db.query(User).filter(
            (User.phone.like("139000002%")) | (User.phone.like("139000003%"))
        ).all()
        for u in test_users:
            db.query(Anniversary).filter(Anniversary.user_id == u.user_id).delete(synchronize_session=False)
            db.query(ContactHoliday).filter(ContactHoliday.user_id == u.user_id).delete(synchronize_session=False)
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
    return _register_and_login(TEST_PHONE)


@pytest.fixture
def auth_headers_2():
    return _register_and_login(TEST_PHONE_2, nickname="纪念日测试用户2")


def _register_and_login(phone, nickname="纪念日测试用户"):
    resp = client.post("/api/v1/auth/register", json={
        "phone": phone,
        "sms_code": "123456",
        "password": TEST_PASSWORD,
        "nickname": nickname,
    })
    assert resp.status_code == 200
    token = resp.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def _create_contact(headers, name="测试妈妈", relationship="母亲"):
    resp = client.post("/api/v1/contacts/", json={
        "name": name,
        "relationship": relationship,
    }, headers=headers)
    assert resp.status_code == 200
    return resp.json()["data"]["contact_id"]


def test_get_templates(auth_headers):
    resp = client.get("/api/v1/anniversaries/templates", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["data"]["list"]
    assert len(items) == 10
    assert items[0]["title_key"] == "birthday"
    assert items[0]["label"] == "生日"


def test_create_anniversary_with_template(auth_headers):
    contact_id = _create_contact(auth_headers)
    resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title_key": "birthday",
        "date": "03-15",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == "生日"
    assert data["anniversary_id"].startswith("A")
    assert data["next_date"] >= date.today().isoformat()


def test_create_anniversary_custom_title(auth_headers):
    contact_id = _create_contact(auth_headers)
    resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "自定义纪念日",
        "date": "12-31",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "自定义纪念日"


def test_create_anniversary_invalid_date(auth_headers):
    contact_id = _create_contact(auth_headers)
    resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "无效日期",
        "date": "13-40",
    }, headers=auth_headers)
    assert resp.status_code == 422


def test_list_anniversaries_by_contact(auth_headers):
    contact_id = _create_contact(auth_headers)
    for d in ["12-31", "01-15", "06-01"]:
        client.post("/api/v1/anniversaries/", json={
            "contact_id": contact_id,
            "title": f"纪念日{d}",
            "date": d,
        }, headers=auth_headers)

    resp = client.get("/api/v1/anniversaries/", params={"contact_id": contact_id}, headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["data"]["list"]
    assert len(items) == 3
    next_dates = [item["next_date"] for item in items]
    assert next_dates == sorted(next_dates)


def test_update_anniversary(auth_headers):
    contact_id = _create_contact(auth_headers)
    create_resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title_key": "birthday",
        "date": "03-15",
    }, headers=auth_headers)
    anniversary_id = create_resp.json()["data"]["anniversary_id"]

    resp = client.put(f"/api/v1/anniversaries/{anniversary_id}", json={
        "date": "07-20",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["month_day"] == "07-20"
    assert data["next_date"][5:10] == "07-20"


def test_delete_anniversary(auth_headers):
    contact_id = _create_contact(auth_headers)
    create_resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title_key": "birthday",
        "date": "03-15",
    }, headers=auth_headers)
    anniversary_id = create_resp.json()["data"]["anniversary_id"]

    resp = client.delete(f"/api/v1/anniversaries/{anniversary_id}", headers=auth_headers)
    assert resp.status_code == 200

    list_resp = client.get("/api/v1/anniversaries/", params={"contact_id": contact_id}, headers=auth_headers)
    ids = [item["anniversary_id"] for item in list_resp.json()["data"]["list"]]
    assert anniversary_id not in ids

    resp = client.delete("/api/v1/anniversaries/AXXXXXXXX", headers=auth_headers)
    assert resp.status_code == 404


def test_list_holidays(auth_headers):
    resp = client.get("/api/v1/holidays/", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["data"]["list"]
    assert len(items) == 9
    for item in items:
        assert item["holiday_id"].startswith("H")
        assert item["name"]
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", item["date"])
        assert isinstance(item["applicable_relationships"], list)

    mothers_day = next(item for item in items if item["name"] == "母亲节")
    month, day = int(mothers_day["date"][5:7]), int(mothers_day["date"][8:10])
    weekday = date.fromisoformat(mothers_day["date"]).weekday()
    assert month == 5
    assert weekday == 6  # Sunday
    assert 8 <= day <= 14  # 第2个星期日


def test_list_holidays_by_relationship(auth_headers):
    resp = client.get("/api/v1/holidays/", params={"relationship": "母亲"}, headers=auth_headers)
    assert resp.status_code == 200
    names = [item["name"] for item in resp.json()["data"]["list"]]
    assert "母亲节" in names
    assert "妇女节" in names
    assert "父亲节" not in names


def test_toggle_holiday_remind(auth_headers):
    contact_id = _create_contact(auth_headers)
    resp = client.put(
        f"/api/v1/holidays/contacts/{contact_id}/holidays/H0004/remind",
        json={"remind_enabled": False},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    resp = client.put(
        f"/api/v1/holidays/contacts/{contact_id}/holidays/H0004/remind",
        json={"remind_enabled": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200


def test_unauthorized():
    resp = client.get("/api/v1/anniversaries/")
    assert resp.status_code == 403


def test_create_anniversary_feb29(auth_headers):
    contact_id = _create_contact(auth_headers)
    resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "闰日纪念日",
        "date": "02-29",
    }, headers=auth_headers)
    assert resp.status_code == 200
    next_date = date.fromisoformat(resp.json()["data"]["next_date"])
    assert next_date.month == 2
    assert next_date.day in (28, 29)


def test_create_anniversary_impossible_date(auth_headers):
    contact_id = _create_contact(auth_headers)
    for bad_date in ["02-30", "04-31"]:
        resp = client.post("/api/v1/anniversaries/", json={
            "contact_id": contact_id,
            "title": "无效日期",
            "date": bad_date,
        }, headers=auth_headers)
        assert resp.status_code == 422, bad_date


def test_create_monthly_anniversary_rolls_to_next_month(auth_headers):
    today = date.today()
    if today.day == 1:
        pytest.skip("当月1号无法构造本月已过的日期")
    contact_id = _create_contact(auth_headers)
    month_day = f"{today.month:02d}-{today.day - 1:02d}"
    resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "月度纪念日",
        "date": month_day,
        "repeat_type": "monthly",
    }, headers=auth_headers)
    assert resp.status_code == 200
    next_date = date.fromisoformat(resp.json()["data"]["next_date"])
    if today.month == 12:
        expected_year, expected_month = today.year + 1, 1
    else:
        expected_year, expected_month = today.year, today.month + 1
    assert (next_date.year, next_date.month) == (expected_year, expected_month)
    assert next_date.day == today.day - 1


def test_create_anniversary_with_other_users_contact(auth_headers, auth_headers_2):
    other_contact_id = _create_contact(auth_headers_2, name="别人的妈妈")
    resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": other_contact_id,
        "title": "越权纪念日",
        "date": "03-15",
    }, headers=auth_headers)
    assert resp.status_code == 404


def test_toggle_remind_other_users_contact(auth_headers, auth_headers_2):
    other_contact_id = _create_contact(auth_headers_2, name="别人的妈妈")
    resp = client.put(
        f"/api/v1/holidays/contacts/{other_contact_id}/holidays/H0004/remind",
        json={"remind_enabled": True},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_toggle_remind_nonexistent_holiday(auth_headers):
    contact_id = _create_contact(auth_headers)
    resp = client.put(
        f"/api/v1/holidays/contacts/{contact_id}/holidays/H9999/remind",
        json={"remind_enabled": True},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_update_soft_deleted_anniversary(auth_headers):
    contact_id = _create_contact(auth_headers)
    create_resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "待删除纪念日",
        "date": "03-15",
    }, headers=auth_headers)
    anniversary_id = create_resp.json()["data"]["anniversary_id"]
    client.delete(f"/api/v1/anniversaries/{anniversary_id}", headers=auth_headers)

    resp = client.put(f"/api/v1/anniversaries/{anniversary_id}", json={
        "title": "更新已删除",
    }, headers=auth_headers)
    assert resp.status_code == 404
