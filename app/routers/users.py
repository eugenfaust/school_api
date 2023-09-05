from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from dependencies import get_current_active_user, get_db
from sql_app import crud, schemas
from sql_app.schemas import User


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/get/", response_model=list[User])
async def read_users(current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db), offset: int | None = None, limit: int | None = None):
    if not current_user.is_super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )
    users = crud.get_users(db, skip=offset, limit=limit)
    return users


@router.post("/create/", response_model=User)
async def create_user(
        user: schemas.UserCreate,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Session = Depends(get_db),
):
    if not current_user.is_super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = crud.create_user(db, user)
    return user


@router.post("/delete/")
async def delete_user(
        user: schemas.UserDelete,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Session = Depends(get_db)
):
    if not current_user.is_super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = crud.delete_user(db, user)
    if user:
        return {"status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error while deleting",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/update/", response_model=schemas.User)
async def update_user(
        user: schemas.UserUpdate,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Session = Depends(get_db)
):
    if not current_user.is_super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no rights",
            headers={"WWW-Authenticate": "Bearer"}
        )
    client = crud.update_user(db, user)
    if client:
        return client
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client not found",
            headers={"WWW-Authenticate": "Bearer"}
        )