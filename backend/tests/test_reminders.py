from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.contact import Contact
from app.models.anniversary import Anniversary
from app.models.holiday import ContactHoliday, SystemHoliday
from app.models.reminder import Reminder
from app.jobs.reminder_job import check_and_generate_reminders

client = TestClient(app)

TEST_PHONE = "13900000401"
TEST_PASSWORD = "testpass123"
TEST_PHONE_2 = "13900000501"


def cleanup_test_data():
    db = SessionLocal()
    try:
        test_users = db.query(User).filter(
            (User.phone.like("139000004%")) | (User.phone.like("139000005%"))
        ).all()
        for u in test_users:
            db.query(Reminder).filter(Reminder.user_id == u.user_id).delete(synchronize_session=False)
            db.query(Anniversary).filter(Anniversary.user_id == u.user_id).delete(synchronize_session=False)
            db.query(ContactHoliday).filter(ContactHoliday.user_id == u.user_id).delete(synchronize_session=False)
            db.query(Contact).filter(Contact.user_id == u.user_id).delete(synchronize_session=False)
            db.delete(u)
        # 测试插入的节假日
        db.query(SystemHoliday).filter(SystemHoliday.holiday_id.like("HTEST%")).delete(synchronize_session=False)
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
    return _register_and_login(TEST_PHONE_2, nickname="提醒测试用户2")


def _register_and_login(phone, nickname="提醒测试用户"):
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


def _get_reminders(headers, **params):
    resp = client.get("/api/v1/reminders/", params=params, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["code"] == 0
    return resp.json()["data"]


def test_list_reminders_empty(auth_headers):
    data = _get_reminders(auth_headers)
    assert "total" in data
    assert isinstance(data["list"], list)
    assert data["total"] == 0


def test_job_generates_personal_reminder(auth_headers):
    contact_id = _create_contact(auth_headers)
    target = date.today() + timedelta(days=5)
    resp = client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "生日",
        "date": target.strftime("%m-%d"),
    }, headers=auth_headers)
    assert resp.status_code == 200

    check_and_generate_reminders()

    data = _get_reminders(auth_headers)
    assert data["total"] == 1
    item = data["list"][0]
    assert item["type"] == "personal"
    assert item["contact_id"] == contact_id
    assert item["event_title"] == "生日"
    assert item["event_date"] == target.isoformat()
    assert item["remind_time"] == target.isoformat() + "T00:00:00"
    assert item["status"] == "unread"
    assert isinstance(item["gifts"], list) and len(item["gifts"]) > 0
    assert item["gifts"]


def test_job_no_duplicate_on_rerun(auth_headers):
    contact_id = _create_contact(auth_headers)
    target = date.today() + timedelta(days=5)
    client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "生日",
        "date": target.strftime("%m-%d"),
    }, headers=auth_headers)

    check_and_generate_reminders()
    check_and_generate_reminders()

    data = _get_reminders(auth_headers)
    assert data["total"] == 1


def test_job_generates_holiday_reminder(auth_headers):
    contact_id = _create_contact(auth_headers, relationship="母亲")
    holiday_date = date.today() + timedelta(days=3)
    db = SessionLocal()
    try:
        db.add(SystemHoliday(
            holiday_id="HTEST0001",
            name="测试节",
            date_rule=holiday_date.strftime("%m-%d"),
            applicable_relationships=["母亲"],
            status=1,
        ))
        db.commit()
    finally:
        db.close()

    resp = client.put(
        f"/api/v1/holidays/contacts/{contact_id}/holidays/HTEST0001/remind",
        json={"remind_enabled": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    check_and_generate_reminders()

    data = _get_reminders(auth_headers, type="holiday")
    assert data["total"] == 1
    item = data["list"][0]
    assert item["holiday_id"] == "HTEST0001"
    assert item["event_title"] == "测试节"
    assert item["event_date"] == holiday_date.isoformat()
    assert item["blessing"]
    assert "测试妈妈" in item["blessing"]


def test_job_rolls_stale_next_date(auth_headers):
    contact_id = _create_contact(auth_headers)
    db = SessionLocal()
    try:
        anniversary = Anniversary(
            anniversary_id="ASTALE001",
            contact_id=contact_id,
            user_id=_user_id(auth_headers),
            title="过期纪念日",
            month_day=(date.today() - timedelta(days=1)).strftime("%m-%d"),
            repeat_type="yearly",
            next_date=date.today() - timedelta(days=1),
        )
        db.add(anniversary)
        db.commit()
    finally:
        db.close()

    check_and_generate_reminders()

    db = SessionLocal()
    try:
        row = db.query(Anniversary).filter(Anniversary.anniversary_id == "ASTALE001").first()
        assert row.next_date >= date.today()
    finally:
        db.close()


def test_mark_read(auth_headers):
    contact_id = _create_contact(auth_headers)
    target = date.today() + timedelta(days=5)
    client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "生日",
        "date": target.strftime("%m-%d"),
    }, headers=auth_headers)
    check_and_generate_reminders()
    reminder_id = _get_reminders(auth_headers)["list"][0]["reminder_id"]

    resp = client.put(f"/api/v1/reminders/{reminder_id}/read", headers=auth_headers)
    assert resp.status_code == 200
    data = _get_reminders(auth_headers, status="read")
    assert data["total"] == 1
    assert data["list"][0]["reminder_id"] == reminder_id

    resp = client.put("/api/v1/reminders/RXXXXXXXX/read", headers=auth_headers)
    assert resp.status_code == 404


def test_regenerate_blessing_and_gifts(auth_headers):
    contact_id = _create_contact(auth_headers)
    target = date.today() + timedelta(days=5)
    client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "生日",
        "date": target.strftime("%m-%d"),
    }, headers=auth_headers)
    check_and_generate_reminders()
    reminder_id = _get_reminders(auth_headers)["list"][0]["reminder_id"]

    resp = client.post(f"/api/v1/reminders/{reminder_id}/blessing", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["blessing"]

    resp = client.post(f"/api/v1/reminders/{reminder_id}/gifts", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"]["gifts"], list)

    resp = client.post("/api/v1/reminders/RXXXXXXXX/blessing", headers=auth_headers)
    assert resp.status_code == 404
    resp = client.post("/api/v1/reminders/RXXXXXXXX/gifts", headers=auth_headers)
    assert resp.status_code == 404


def test_mark_read_other_users_reminder(auth_headers, auth_headers_2):
    contact_id = _create_contact(auth_headers)
    target = date.today() + timedelta(days=5)
    client.post("/api/v1/anniversaries/", json={
        "contact_id": contact_id,
        "title": "生日",
        "date": target.strftime("%m-%d"),
    }, headers=auth_headers)
    check_and_generate_reminders()
    reminder_id = _get_reminders(auth_headers)["list"][0]["reminder_id"]

    resp = client.put(f"/api/v1/reminders/{reminder_id}/read", headers=auth_headers_2)
    assert resp.status_code == 404


def _user_id(headers):
    # 从 token 解析 user_id 太绕，直接查库
    db = SessionLocal()
    try:
        return db.query(User).filter(User.phone == TEST_PHONE).first().user_id
    finally:
        db.close()


def test_unauthorized():
    resp = client.get("/api/v1/reminders/")
    assert resp.status_code == 403
