from sqlalchemy import Column, BigInteger, String, Date, DateTime, SmallInteger
from sqlalchemy.sql import func

from app.core.database import Base


class AnniversaryTemplate(Base):
    __tablename__ = "t_anniversary_template"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title_key = Column(String(32), unique=True, nullable=False)
    label = Column(String(50), nullable=False)
    default_repeat = Column(String(20), default="yearly")
    sort_order = Column(BigInteger, default=0)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())


class Anniversary(Base):
    __tablename__ = "t_anniversary"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    anniversary_id = Column(String(32), unique=True, nullable=False, index=True)
    contact_id = Column(String(32), nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    title = Column(String(50), nullable=False)
    title_key = Column(String(32), nullable=True)
    month_day = Column(String(5), nullable=False)
    repeat_type = Column(String(20), nullable=False)
    next_date = Column(Date, nullable=False)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
