import asyncio
from typing import Annotated, Optional

import aiofiles
from fastapi import Form, UploadFile, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from bot import send_files
from dependencies import get_current_active_user, get_db
from sql_app import schemas, crud
from sql_app.schemas import User


router = APIRouter(
    prefix="/homework",
    tags=["homework"],
)


@router.post("/create/", response_model=schemas.Homework)
async def create_homework(name: Annotated[str, Form()], files: list[UploadFile],
                          user_id: Annotated[int, Form()],
                          current_user: Annotated[User, Depends(get_current_active_user)],
                          db: Session = Depends(get_db)):
    if not current_user.is_super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )
    filepaths = []
    for file in files:
        filepath = f'docs/{file.filename}'
        async with aiofiles.open(filepath, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            filepaths.append(filepath)
    homework = crud.create_homework(db, name, user_id, filepaths)
    if homework.user.tg_id:
        asyncio.create_task(send_files(homework.user.tg_id, 'Было добавлено новое домашнее задание:\n{}'
                                       .format(homework.name), homework.files))
    return homework


@router.get("/get/", response_model=list[schemas.Homework])
async def get_homeworks(current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db), user_id: int | None = None, offset: int = 0):
    if current_user.is_super or current_user.id == user_id:
        return crud.get_homeworks(db, user_id=user_id, skip=offset)
    elif not user_id:
        return crud.get_homeworks(db, user_id=current_user.id, skip=offset)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get('/search/', response_model=list[schemas.Homework])
async def search_homework(q: str, current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db), offset: int = 0):
    return crud.search_homework(db, current_user.id, q, offset)


@router.get("/delete/{homework_id}")
async def delete_homework(homework_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db)):
    if current_user.is_super:
        crud.delete_homework(db, homework_id)
        return {"status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/update/", response_model=schemas.Homework)
async def update_homework(
        homework_id: Annotated[int, Form()],
        current_user: Annotated[User, Depends(get_current_active_user)],
        name: Optional[str] = Form(None),
        files: Optional[list[UploadFile]] = Form(None),
        db: Session = Depends(get_db)
):
    if not current_user.is_super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )
    filepaths = []
    if files:
        for file in files:
            filepath = f'docs/{file.filename}'
            async with aiofiles.open(filepath, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
                filepaths.append(filepath)
    homework = crud.update_homework(db, name, homework_id, filepaths)
    if homework:
        return homework
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Homework not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
