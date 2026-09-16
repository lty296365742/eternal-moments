from sqlalchemy import Column, BigInteger, String, Date, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Reminder(Base):
    __tablename__ = "t_reminder"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reminder_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    contact_id = Column(String(32), nullable=False)
    type = Column(String(20), nullable=False)
    anniversary_id = Column(String(32), nullable=True)
    holiday_id = Column(String(32), nullable=True)
    event_title = Column(String(50), nullable=False)
    event_date = Column(Date, nullable=False)
    remind_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="unread")
    blessing = Column(Text, nullable=True)
    gifts = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
