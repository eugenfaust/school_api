import datetime
import random
import string

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_tg_hash(db: Session, hash: str):
    return db.query(models.User).filter(models.User.tg_hash == hash).first()


def get_users(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.User).filter(models.User.is_super == False).order_by(models.User.created.desc()).offset(skip).limit(limit).all()


def delete_user(db: Session, user: schemas.UserDelete):
    try:
        db.query(models.User).filter(models.User.id == user.id).delete()
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False


def create_user(db: Session, user: schemas.UserCreate, is_super=False):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, is_super=is_super,
                          full_name=user.full_name)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        credentials_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already created",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception


def update_user(db: Session, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    if db_user:
        if user.full_name:
            db_user.full_name = user.full_name
        if user.username:
            db_user.username = user.username
        if user.balance:
            db_user.balance = user.balance
        if user.lesson_price:
            db_user.lesson_price = user.lesson_price
        if user.password:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(user.password)
            db_user.hashed_password = hashed_password
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        return None


def change_user_password(db: Session, user_id: int, new_password: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(new_password)
        db_user.hashed_password = hashed_password
        db.commit()
        return True
    else:
        return False


def create_schedule(db: Session, schedule: schemas.ScheduleCreate):
    db_schedule = models.Schedule(user_id=schedule.user_id, note=schedule.note, scheduled_at=schedule.scheduled_at)
    db.add(db_schedule)
    try:
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except IntegrityError as e:
        credentials_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IntegrityError",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception


def get_schedules(db: Session, active, user_id: int = -1, skip: int = 0, limit: int = 20):
    filter_query = datetime.datetime.now()
    if not active:
        filter_query = filter_query.replace(1970)
    if user_id == -1:
        return db.query(models.Schedule).join(models.Schedule.user).filter(models.Schedule.scheduled_at > filter_query).order_by(models.Schedule.scheduled_at.desc()).offset(skip).limit(limit).all()
    else:
        return db.query(models.Schedule).filter((models.Schedule.user_id == user_id) & (models.Schedule.scheduled_at > filter_query)).order_by(models.Schedule.scheduled_at.desc()).offset(skip).limit(limit).all()


def get_active_schedules_with_tg(db: Session, cur_date):
    return db.query(models.Schedule).join(models.User).filter((models.Schedule.tg_notified == False) & (models.Schedule.scheduled_at > cur_date) & (models.User.tg_id != None)).all()


def delete_schedule(db: Session, schedule_id: int):
    try:
        db.query(models.Schedule).filter(models.Schedule.id == schedule_id).delete()
        db.commit()
        return True
    except Exception as e:
        return False


def update_schedule(db: Session, schedule: schemas.ScheduleUpdate):
    db_schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule.id).first()
    if db_schedule:
        db_schedule.scheduled_at = schedule.scheduled_at
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    else:
        return None


def get_homeworks(db: Session, user_id: int = -1, skip: int = 0, limit: int = 20):
    if user_id == -1:
        return db.query(models.Homework).join(models.Homework.user).order_by(models.Homework.created_at.desc()).offset(skip).limit(limit).all()
    else:
        return db.query(models.Homework).filter(models.Homework.user_id == user_id).order_by(models.Homework.created_at.desc()).offset(skip).limit(limit).all()


def search_homework(db: Session, user_id: int, query: str, offset):
    return db.query(models.Homework).filter((models.Homework.user_id == user_id) & (models.Homework.name.ilike(f"%{query}%"))).order_by(models.Homework.created_at.desc()).offset(offset).limit(20).all()


def delete_homework(db: Session, homework_id: int):
    try:
        db.query(models.Homework).filter(models.Homework.id == homework_id).delete()
        db.commit()
        return True
    except Exception as e:
        return False


def get_notes(db: Session, user_id: int = -1, skip: int = 0, limit: int = 20):
    if user_id == -1:
        return db.query(models.Notes).join(models.Notes.user).order_by(models.Notes.created_at.desc()).offset(skip).limit(limit).all()
    else:
        return db.query(models.Notes).filter(models.Notes.user_id == user_id).order_by(models.Notes.created_at.desc()).offset(skip).limit(limit).all()


def search_notes(db: Session, user_id: int, query: str, offset):
    return db.query(models.Notes).filter((models.Notes.user_id == user_id) & (models.Notes.name.ilike(f"%{query}%"))).order_by(models.Notes.created_at.desc()).offset(offset).limit(20).all()


def delete_note(db: Session, note_id: int):
    try:
        db.query(models.Notes).filter(models.Notes.id == note_id).delete()
        db.commit()
        return True
    except Exception as e:
        return False


def update_homework(db: Session, name, homework_id: int, files):
    db_homework = db.query(models.Homework).filter(models.Homework.id == homework_id).first()
    if db_homework:
        if name:
            db_homework.name = name
        if len(files) > 0:
            db_homework.files = files
        db.commit()
        db.refresh(db_homework)
        return db_homework
    else:
        return None


def create_homework(db: Session, name, user_id, files):
    db_homework = models.Homework(user_id=user_id, name=name, files=files)
    db.add(db_homework)
    try:
        db.commit()
        db.refresh(db_homework)
        return db_homework
    except IntegrityError:
        credentials_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IntegrityError",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception


def create_note(db: Session, name, user_id, files):
    db_note = models.Notes(user_id=user_id, name=name, files=files)
    db.add(db_note)
    try:
        db.commit()
        db.refresh(db_note)
        return db_note
    except IntegrityError:
        credentials_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IntegrityError",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception


def update_note(db: Session, name, note_id: int, files):
    db_note = db.query(models.Notes).filter(models.Notes.id == note_id).first()
    if db_note:
        if name:
            db_note.name = name
        if len(files) > 0:
            db_note.files = files
        db.commit()
        db.refresh(db_note)
        return db_note
    else:
        return None