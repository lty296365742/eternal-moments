from datetime import date

from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.models.holiday import SystemHoliday, ContactHoliday


def calculate_holiday_date(rule: str, year: int) -> date:
    """根据规则计算某年的节假日日期。
    支持：
    - "MM-DD" 固定日期，如 "05-10"
    - "MM-WEEKDAY-N" 第N个星期X，如 "05-SUN-2"（5月第2个星期日）、
      "06-SUN-3"（6月第3个星期日）、"11-THU-4"（11月第4个星期四）
    复杂农历规则后续迭代。
    """
    if "-" in rule and len(rule) == 5:
        month, day = map(int, rule.split("-"))
        return date(year, month, day)
    parts = rule.split("-")
    if len(parts) == 3:
        month = int(parts[0])
        weekday_name, nth = parts[1], int(parts[2])
        weekdays = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}
        target = weekdays[weekday_name]
        first = date(year, month, 1)
        offset = (target - first.weekday()) % 7
        return date(year, month, 1 + offset + (nth - 1) * 7)
    raise ValueError(f"无法解析的节假日规则: {rule}")


class HolidayService:
    def __init__(self, db: Session):
        self.db = db

    def get_holidays(self, relationship: str = None):
        query = self.db.query(SystemHoliday).filter(SystemHoliday.status == 1)
        if relationship:
            # PG json 类型不支持 contains，转为 jsonb 使用 @> 操作符
            query = query.filter(
                cast(SystemHoliday.applicable_relationships, JSONB).contains([relationship])
            )
        return query.all()

    def serialize_holiday(self, holiday: SystemHoliday, year: int = None) -> dict:
        year = year or date.today().year
        return {
            "holiday_id": holiday.holiday_id,
            "name": holiday.name,
            "date": calculate_holiday_date(holiday.date_rule, year).isoformat(),
            "applicable_relationships": holiday.applicable_relationships,
            "description": holiday.description,
        }

    def set_remind_enabled(self, user_id: str, contact_id: str, holiday_id: str, enabled: bool):
        record = self.db.query(ContactHoliday).filter(
            ContactHoliday.user_id == user_id,
            ContactHoliday.contact_id == contact_id,
            ContactHoliday.holiday_id == holiday_id
        ).first()
        if not record:
            record = ContactHoliday(
                contact_id=contact_id,
                holiday_id=holiday_id,
                user_id=user_id,
                remind_enabled=1 if enabled else 0
            )
            self.db.add(record)
        else:
            record.remind_enabled = 1 if enabled else 0
        self.db.commit()
        return record
