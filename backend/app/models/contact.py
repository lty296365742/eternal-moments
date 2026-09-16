from sqlalchemy import Column, BigInteger, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Contact(Base):
    __tablename__ = "t_contact"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contact_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    avatar = Column(String(500), nullable=True)
    relationship = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
