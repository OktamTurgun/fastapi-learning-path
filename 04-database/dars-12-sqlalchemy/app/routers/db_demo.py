"""
Engine va Session'ning ishlashini "qo'lda" ko'rish uchun demo.
Haqiqiy model (Dars 13'da) hali yo'q, shuning uchun oddiy SQL
orqali sinaymiz — bu SQLAlchemy'ning "past darajadagi" (raw SQL)
imkoniyatini ham ko'rsatadi.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/db-check")
def check_db_connection(db: Session = Depends(get_db)):
    """
    Engine va Session to'g'ri ishlayotganini tekshirish uchun
    eng oddiy so'rov — "SELECT 1".
    """
    result = db.execute(text("SELECT 1"))
    value = result.scalar()
    return {"db_connected": True, "test_query_result": value}


@router.get("/db-session-info")
def session_info(db: Session = Depends(get_db)):
    """
    Session obyekti haqida ma'lumot — bu sizga get_db() qanday
    ishlayotganini "ko'rish" imkonini beradi.
    """
    return {
        "session_class": type(db).__name__,
        "is_active": db.is_active,
        "bind_url": str(db.get_bind().url),
    }