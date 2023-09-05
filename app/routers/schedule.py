import asyncio
import logging
from typing import Annotated

import pytz as pytz
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from bot import send_text
from sql_app import crud, schemas
from dependencies import get_db, get_current_active_user
from sql_app.models import User

router = APIRouter(
    prefix="/schedule",
    tags=["schedule"],
)


@router.post("/create/")
async def create_schedule(schedule: schemas.ScheduleCreate,
                          current_user: Annotated[User, Depends(get_current_active_user)],
                          db: Session = Depends(get_db)):
    if not current_user.is_super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )
    db_schedule = crud.create_schedule(db, schedule)
    if db_schedule.user.tg_id:
        tzdata = pytz.timezone('Europe/Moscow')
        asyncio.create_task(send_text(db_schedule.user.tg_id, "Запланировано новое занятие на {}"
                                      .format(schedule.scheduled_at.astimezone(tzdata).strftime("%d.%m.%Y, %H:%M:%S"))))
    return db_schedule


@router.get("/get/", response_model=list[schemas.Schedule])
async def get_schedules(current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db), user_id: int | None = None, active: bool = False):
    if current_user.is_super or current_user.id == user_id:
        return crud.get_schedules(db, user_id=user_id, active=active)
    elif not user_id:
        return crud.get_schedules(db, user_id=current_user.id, active=active)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/delete/{schedule_id}")
async def delete_schedule(schedule_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db)):
    if current_user.is_super:
        crud.delete_schedule(db, schedule_id=schedule_id)
        return {"status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/update/", response_model=schemas.Schedule)
async def update_schedule(schedule: schemas.ScheduleUpdate, current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db)):
    if current_user.is_super:
        return crud.update_schedule(db, schedule)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )



