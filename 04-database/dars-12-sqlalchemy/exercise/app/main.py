from fastapi import FastAPI
from app.routers import library_db

app = FastAPI(title="Library Database Demo", version="1.0.0")

app.include_router(library_db.router, tags=["library_db"])

@app.get("/")
def root():
  return {"message": "Library Database demo ishlamoqada."}

