import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.reminder import Reminder
from app.services.ai_service import get_ai_client


class ReminderService:
    def __init__(self, db: Session):
        self.db = db

    def _get_contact(self, user_id: str, contact_id: str) -> Contact:
        contact = self.db.query(Contact).filter(
            Contact.contact_id == contact_id,
            Contact.user_id == user_id
        ).first()
        if not contact:
            raise ValueError("联系人不存在")
        return contact

    def _exists(self, user_id: str, contact_id: str, type_: str,
                event_date, anniversary_id=None, holiday_id=None) -> bool:
        query = self.db.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.contact_id == contact_id,
            Reminder.type == type_,
            Reminder.event_date == event_date
        )
        if type_ == "personal":
            query = query.filter(Reminder.anniversary_id == anniversary_id)
        else:
            query = query.filter(Reminder.holiday_id == holiday_id)
        return self.db.query(query.exists()).scalar()

    def get_reminders(self, user_id: str, type_: str = None, status: str = None,
                      page: int = 1, page_size: int = 20):
        query = self.db.query(Reminder).filter(Reminder.user_id == user_id)
        if type_:
            query = query.filter(Reminder.type == type_)
        if status:
            query = query.filter(Reminder.status == status)
        total = query.count()
        reminders = (
            query.order_by(Reminder.remind_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return total, reminders

    def get_reminder(self, user_id: str, reminder_id: str) -> Reminder:
        reminder = self.db.query(Reminder).filter(
            Reminder.reminder_id == reminder_id,
            Reminder.user_id == user_id
        ).first()
        if not reminder:
            raise ValueError("提醒不存在")
        return reminder

    def mark_read(self, user_id: str, reminder_id: str) -> Reminder:
        reminder = self.get_reminder(user_id, reminder_id)
        reminder.status = "read"
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def generate_personal_reminder(self, anniversary) -> Reminder:
        """5天规则：事件日期前5天生成提醒，附礼物推荐"""
        contact = self._get_contact(anniversary.user_id, anniversary.contact_id)
        if self._exists(anniversary.user_id, anniversary.contact_id, "personal",
                        anniversary.next_date, anniversary_id=anniversary.anniversary_id):
            return None

        client = get_ai_client()
        gifts = client.recommend_gifts(contact.relationship, contact.name, anniversary.title)
        reminder = Reminder(
            reminder_id=f"R{uuid.uuid4().hex[:8].upper()}",
            user_id=anniversary.user_id,
            contact_id=anniversary.contact_id,
            type="personal",
            anniversary_id=anniversary.anniversary_id,
            event_title=anniversary.title,
            event_date=anniversary.next_date,
            remind_time=datetime.combine(
                anniversary.next_date - timedelta(days=5), datetime.min.time()),
            status="unread",
            gifts=gifts,
        )
        self.db.add(reminder)
        self.db.commit()
        return reminder

    def generate_holiday_reminder(self, user_id: str, contact_id: str,
                                  holiday, holiday_date) -> Reminder:
        """3天规则：节假日日期前3天生成提醒，附祝福语"""
        contact = self._get_contact(user_id, contact_id)
        if self._exists(user_id, contact_id, "holiday", holiday_date,
                        holiday_id=holiday.holiday_id):
            return None

        client = get_ai_client()
        blessing = client.generate_blessing(
            contact.relationship, contact.name, holiday.name, holiday_date.isoformat()
        )
        reminder = Reminder(
            reminder_id=f"R{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            contact_id=contact_id,
            type="holiday",
            holiday_id=holiday.holiday_id,
            event_title=holiday.name,
            event_date=holiday_date,
            remind_time=datetime.combine(
                holiday_date - timedelta(days=3), datetime.min.time()),
            status="unread",
            blessing=blessing,
        )
        self.db.add(reminder)
        self.db.commit()
        return reminder

    def regenerate_blessing(self, user_id: str, reminder_id: str) -> str:
        reminder = self.get_reminder(user_id, reminder_id)
        contact = self._get_contact(user_id, reminder.contact_id)
        client = get_ai_client()
        reminder.blessing = client.generate_blessing(
            contact.relationship, contact.name, reminder.event_title,
            reminder.event_date.isoformat()
        )
        self.db.commit()
        return reminder.blessing

    def regenerate_gifts(self, user_id: str, reminder_id: str) -> list:
        reminder = self.get_reminder(user_id, reminder_id)
        contact = self._get_contact(user_id, reminder.contact_id)
        client = get_ai_client()
        reminder.gifts = client.recommend_gifts(
            contact.relationship, contact.name, reminder.event_title
        )
        self.db.commit()
        return reminder.gifts
