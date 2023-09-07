import decimal
from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    pass


class UserDelete(UserBase):
    id: int


class UserCreate(UserBase):
    username: str
    full_name: str = None
    tg_id: int = None
    password: str


class UserUpdate(UserBase):
    id: int
    full_name: str = None
    username: str = None
    lesson_price: decimal.Decimal = None
    balance: decimal.Decimal = None
    password: str = None


class User(UserBase):
    id: int
    tg_id: int | None
    is_active: bool
    username: str
    tg_hash: str
    is_super: bool
    lesson_price: decimal.Decimal
    balance: decimal.Decimal
    full_name: str | None
    created: datetime

    class Config:
        orm_mode = True


class Schedule(BaseModel):
    id: int
    user_id: int
    user: User
    note: str | None
    tg_notified: bool
    scheduled_at: datetime

    class Config:
        orm_mode = True


class ScheduleUpdate(BaseModel):
    id: int
    scheduled_at: datetime


class ScheduleCreate(BaseModel):
    user_id: int
    scheduled_at: datetime
    note: str = None


class Homework(BaseModel):
    id: int
    user_id: int
    user: User
    files: list[str]
    name: str
    created_at: datetime

    class Config:
        orm_mode = True


class HomeworkCreate(BaseModel):
    user_id: int
    name: str


class HomeworkUpdate(UserBase):
    id: int
    name: str = None
    files: list[str] = None


class Notes(BaseModel):
    id: int
    user_id: int
    user: User
    files: list[str]
    name: str
    created_at: datetime

    class Config:
        orm_mode = True


class NotesCreate(BaseModel):
    user_id: int
    name: str
