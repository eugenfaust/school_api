import asyncio
from typing import Annotated, Optional

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile
from sqlalchemy.orm import Session
from starlette import status

from bot import send_files
from sql_app import crud, schemas
from dependencies import get_db, get_current_active_user
from sql_app.models import User

router = APIRouter(
    prefix="/note",
    tags=["note"],
)


@router.post("/create/", response_model=schemas.Notes)
async def create_note(name: Annotated[str, Form()], files: list[UploadFile],
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
    note = crud.create_note(db, name, user_id, filepaths)
    if note.user.tg_id:
        asyncio.create_task(send_files(note.user.tg_id, 'Был добавлен новый конспект:\n{}'
                                       .format(note.name), note.files))
    return note


@router.get("/get/", response_model=list[schemas.Notes])
async def get_notes(current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db), user_id: int | None = None, offset: int = 0):
    if current_user.is_super or current_user.id == user_id:
        return crud.get_notes(db, user_id, offset)
    elif not user_id:
        return crud.get_notes(db, current_user.id, offset)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get('/search/', response_model=list[schemas.Notes])
async def search_note(q: str, current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db), offset: int = 0):
    return crud.search_notes(db, current_user.id, q, offset)


@router.get("/delete/{note_id}")
async def delete_note(note_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                        db: Session = Depends(get_db)):
    if current_user.is_super:
        crud.delete_note(db, note_id)
        return {"status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/update/", response_model=schemas.Notes)
async def update_note(
        note_id: Annotated[int, Form()],
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
    homework = crud.update_note(db, name, note_id, filepaths)
    if homework:
        return homework
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note not found",
            headers={"WWW-Authenticate": "Bearer"}
        )