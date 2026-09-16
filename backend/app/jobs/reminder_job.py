from datetime import date, timedelta

from app.core.database import SessionLocal
from app.models.anniversary import Anniversary
from app.models.holiday import ContactHoliday, SystemHoliday
from app.services.anniversary_service import AnniversaryService
from app.services.holiday_service import calculate_holiday_date
from app.services.reminder_service import ReminderService

PERSONAL_AHEAD_DAYS = 5
HOLIDAY_AHEAD_DAYS = 3


def check_and_generate_reminders():
    db = SessionLocal()
    try:
        today = date.today()
        service = ReminderService(db)

        # 个人纪念日：提前5天提醒；next_date 已过期时先重算并持久化
        anniversaries = db.query(Anniversary).filter(Anniversary.status == 1).all()
        anniversary_service = AnniversaryService(db)
        rolled = False
        for anniversary in anniversaries:
            if anniversary.next_date < today:
                anniversary.next_date = anniversary_service.calculate_next_date(
                    anniversary.month_day, anniversary.repeat_type
                )
                rolled = True
            if 0 <= (anniversary.next_date - today).days <= PERSONAL_AHEAD_DAYS:
                service.generate_personal_reminder(anniversary)
        if rolled:
            db.commit()

        # 节假日：提前3天提醒
        records = db.query(ContactHoliday).filter(ContactHoliday.remind_enabled == 1).all()
        for record in records:
            holiday = db.query(SystemHoliday).filter(
                SystemHoliday.holiday_id == record.holiday_id,
                SystemHoliday.status == 1
            ).first()
            if not holiday:
                continue
            holiday_date = calculate_holiday_date(holiday.date_rule, today.year)
            if 0 <= (holiday_date - today).days <= HOLIDAY_AHEAD_DAYS:
                service.generate_holiday_reminder(
                    record.user_id, record.contact_id, holiday, holiday_date
                )
    finally:
        db.close()


def start_scheduler():
    # 禁止在测试环境启动
    import sys
    if "pytest" in sys.modules:
        return
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_generate_reminders, "cron", hour=9, minute=0)
    scheduler.start()
