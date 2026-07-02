"""
Dars 01 — FastAPI nima?
Eng oddiy FastAPI ilovasi.
"""

from fastapi import FastAPI

# FastAPI ilovasini yaratish — bu butun API'ning "yuragi"
app = FastAPI(
    title="Mening birinchi FastAPI ilovam",
    description="Dars 01 uchun demo API",
    version="1.0.0",
)


# Eng oddiy endpoint — GET so'rov "/" manziliga kelganda ishlaydi
@app.get("/")
def root():
    return {"message": "Salom, FastAPI dunyosi!"}


# Ikkinchi endpoint — Django DRF'dagi kabi, lekin ancha qisqa yozilishi bilan farq qiladi
@app.get("/about")
def about():
    return {
        "framework": "FastAPI",
        "asos": "Starlette + Pydantic",
        "afzalligi": "Tezkor, avtomatik validatsiya, avtomatik docs",
    }


# Ishga tushirish uchun terminalda:
# uvicorn main:app --reload
#
# --reload flag: kod o'zgarganda serverni avtomatik qayta ishga tushiradi
# (development uchun juda qulay, production'da ishlatilmaydi)