from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./library_demo.db"

engine = create_engine(
  DATABASE_URL,
  connect_args={"check_same_thread": False}, 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
  """
    - Session ochiladi
    - Endpoint funksiyasiga beriladi
    - Endpoint tugagach (xato bo'lsa ham) avtomatik yopiladi
  """
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
