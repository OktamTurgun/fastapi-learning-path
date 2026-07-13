from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()

@router.get("/library/db-check")
def check_db_connection(db: Session = Depends(get_db)):
    """
    Engine va Session to'g'ri ishlayotganini tekshirish uchun
    eng oddiy so'rov — "SELECT 1".
    """
    result = db.execute(text("SELECT 1"))
    value = result.scalar()
    return {"db_connected": True, "test_query_result": value}

@router.get("/library/sqlite-version")
def get_db_version(db: Session = Depends(get_db)):
    """
    Database versiyasini olish uchun so'rov.
    """
    result = db.execute(text("SELECT sqlite_version()"))
    version = result.scalar()
    return {"sqlite_version": version}
