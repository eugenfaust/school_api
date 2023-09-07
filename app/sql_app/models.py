import random
import string
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func, ARRAY, BigInteger, DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column, backref

from .database import Base


def generate_tg_hash():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(12))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(BigInteger, nullable=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    tg_hash = Column(String, default=generate_tg_hash)
    is_active = Column(Boolean, default=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    is_super = Column(Boolean, default=False)
    balance = Column(DECIMAL(), default=0)
    lesson_price = Column(DECIMAL(), default=500)


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True, index=True)
    user_id = mapped_column(ForeignKey('users.id', ondelete="cascade"))
    user: Mapped["User"] = relationship(backref=backref('schedules', passive_deletes=True))
    note = Column(String, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    tg_notified = Column(Boolean, default=False)


class Homework(Base):
    __tablename__ = 'homework'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = mapped_column(ForeignKey('users.id', ondelete="cascade"))
    user: Mapped["User"] = relationship(backref=backref('homeworks', passive_deletes=True))
    files = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship(backref=backref('notes', passive_deletes=True))
    files = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
