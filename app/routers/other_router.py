from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from sqlalchemy import text

from app.dependencies import get_db
from app.database import Base, engine


router = APIRouter()


@router.get("/migrate", name="dev:migrate", status_code=status.HTTP_200_OK)
def migrate(drop=None, db: Session = Depends(get_db)) -> str:
    if drop is not None:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return "migrating..."


@router.get("/ping_bd", name="dev:ping_bd", status_code=status.HTTP_200_OK)
def ping_bd(db: Session = Depends(get_db)) -> dict:
    result = db.execute(text("SELECT 1")).first()
    return {"pong_db": result[0]}


@router.get("/ping", name="dev:ping", status_code=status.HTTP_200_OK)
async def ping() -> str:
    return "pong"
