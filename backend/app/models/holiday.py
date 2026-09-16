from sqlalchemy import Column, BigInteger, String, DateTime, SmallInteger, JSON, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class SystemHoliday(Base):
    __tablename__ = "t_system_holiday"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    holiday_id = Column(String(32), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    date_rule = Column(String(100), nullable=False)
    applicable_relationships = Column(JSON, nullable=False)
    description = Column(String(200), nullable=True)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ContactHoliday(Base):
    __tablename__ = "t_contact_holiday"
    __table_args__ = (
        UniqueConstraint("contact_id", "holiday_id", name="uq_contact_holiday"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contact_id = Column(String(32), nullable=False, index=True)
    holiday_id = Column(String(32), nullable=False)
    user_id = Column(String(32), nullable=False, index=True)
    remind_enabled = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
