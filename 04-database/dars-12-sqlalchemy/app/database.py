"""
Dars 12 — SQLAlchemy Engine va Session sozlamalari
Bu fayl keyingi barcha modullarda (Dars 13-17, Auth, Delivery API)
deyarli o'zgarishsiz qayta ishlatiladi.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./dars12_demo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # faqat SQLite uchun
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dars 07'dagi yield dependency naqshi:
    - Session ochiladi
    - Endpoint funksiyasiga beriladi
    - Endpoint tugagach (xato bo'lsa ham) avtomatik yopiladi
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()