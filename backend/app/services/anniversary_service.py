import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.anniversary import Anniversary, AnniversaryTemplate
from app.schemas.anniversary import AnniversaryCreate, AnniversaryUpdate


class AnniversaryService:
    def __init__(self, db: Session):
        self.db = db

    def get_templates(self):
        return self.db.query(AnniversaryTemplate).filter(
            AnniversaryTemplate.status == 1
        ).order_by(AnniversaryTemplate.sort_order).all()

    def calculate_next_date(self, month_day: str, repeat_type: str) -> date:
        today = date.today()
        month, day = map(int, month_day.split("-"))

        def safe_date(year: int) -> date:
            try:
                return date(year, month, day)
            except ValueError:
                # 2月29日纪念日：非闰年提前到2月28日
                return date(year, month, day - 1)

        if repeat_type == "monthly":
            year, m = today.year, today.month
            candidate_this_month = None
            try:
                candidate_this_month = date(year, m, day)
            except ValueError:
                # 当月没有这一天（如31日遇到小月），顺延到月末
                import calendar
                candidate_this_month = date(year, m, calendar.monthrange(year, m)[1])
            if candidate_this_month >= today:
                return candidate_this_month
            if m == 12:
                year, m = year + 1, 1
            else:
                m += 1
            try:
                return date(year, m, day)
            except ValueError:
                import calendar
                return date(year, m, calendar.monthrange(year, m)[1])

        candidate = safe_date(today.year)
        if candidate < today:
            candidate = safe_date(today.year + 1)
        return candidate

    def create_anniversary(self, user_id: str, data: AnniversaryCreate) -> Anniversary:
        from app.models.contact import Contact
        contact = self.db.query(Contact).filter(
            Contact.contact_id == data.contact_id,
            Contact.user_id == user_id
        ).first()
        if not contact:
            raise ValueError("联系人不存在")

        template = None
        if data.title_key:
            template = self.db.query(AnniversaryTemplate).filter(
                AnniversaryTemplate.title_key == data.title_key
            ).first()

        title = template.label if template else (data.title or "纪念日")
        repeat_type = data.repeat_type or (template.default_repeat if template else "yearly")
        next_date = self.calculate_next_date(data.date, repeat_type)

        anniversary = Anniversary(
            anniversary_id=f"A{uuid.uuid4().hex[:8].upper()}",
            contact_id=data.contact_id,
            user_id=user_id,
            title=title,
            title_key=data.title_key,
            month_day=data.date,
            repeat_type=repeat_type,
            next_date=next_date,
        )
        self.db.add(anniversary)
        self.db.commit()
        self.db.refresh(anniversary)
        return anniversary

    def get_anniversaries(self, user_id: str, contact_id: str = None):
        query = self.db.query(Anniversary).filter(
            Anniversary.user_id == user_id,
            Anniversary.status == 1
        )
        if contact_id:
            query = query.filter(Anniversary.contact_id == contact_id)
        return query.order_by(Anniversary.next_date).all()

    def update_anniversary(self, user_id: str, anniversary_id: str, data: AnniversaryUpdate) -> Anniversary:
        anniversary = self.db.query(Anniversary).filter(
            Anniversary.anniversary_id == anniversary_id,
            Anniversary.user_id == user_id,
            Anniversary.status == 1
        ).first()
        if not anniversary:
            raise ValueError("纪念日不存在")

        update_data = data.dict(exclude_unset=True)
        if "date" in update_data:
            anniversary.month_day = update_data.pop("date")
            anniversary.next_date = self.calculate_next_date(anniversary.month_day, anniversary.repeat_type)
        if "title_key" in update_data:
            template = self.db.query(AnniversaryTemplate).filter(
                AnniversaryTemplate.title_key == update_data["title_key"]
            ).first()
            if template:
                anniversary.title = template.label
        for key, value in update_data.items():
            setattr(anniversary, key, value)

        self.db.commit()
        self.db.refresh(anniversary)
        return anniversary

    def delete_anniversary(self, user_id: str, anniversary_id: str):
        anniversary = self.db.query(Anniversary).filter(
            Anniversary.anniversary_id == anniversary_id,
            Anniversary.user_id == user_id
        ).first()
        if not anniversary:
            raise ValueError("纪念日不存在")
        anniversary.status = 0
        self.db.commit()
