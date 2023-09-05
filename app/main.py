from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import schedule, users, note, homework, files, token

from sql_app import models, crud, schemas
from sql_app.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
# Routers on every path
app.include_router(schedule.router)
app.include_router(files.router)
app.include_router(homework.router)
app.include_router(note.router)
app.include_router(token.router)
app.include_router(users.router)
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create default user
try:
    crud.create_user(next(get_db()), schemas.UserCreate(username="admin", password="12345678"), is_super=True)
except HTTPException:
    pass
