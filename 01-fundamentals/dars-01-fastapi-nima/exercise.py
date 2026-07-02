"""
Dars 01 — Mustaqil mashq

Vazifa:
1. Yangi FastAPI ilova yarating (app nomi: "app").
2. "/salom" manzilida GET endpoint yarating — u sizning ismingiz va
   FastAPI'ni nechanchi kun o'rganayotganingizni JSON qilib qaytarsin.
   Masalan: {"ism": "Uktam", "kun": 1}
3. "/haqida-men" manzilida GET endpoint yarating — u sizning
   texnik stack'ingiz haqida ma'lumot qaytarsin (Python, Django, DRF va h.k.)
4. Serverni ishga tushiring va /docs orqali ikkala endpointni ham
   brauzerda sinab ko'ring.

Bonus (ixtiyoriy):
5. Root manzilida ("/") FastAPI haqida bitta qiziqarli fakt qaytaring —
   buni internetdan izlab toping.
"""

from fastapi import FastAPI

app = FastAPI(
  title="My first FastAPI exercise API",
  description="Demo API for Lesson 01",
  version="1.0.0"
)

# TODO: shu yerga "/salom" endpointini yozing
@app.get("/salom")
def root():
  return {"ism": "Ali", "kun": 1}


# TODO: shu yerga "/haqida-men" endpointini yozing
@app.get("/haqida-men")
def about():
  return {
        "stack": ["Python", "Django", "DRF", "PostgreSQL", "Redis", "Celery", "Docker"],
        "hozir": "FastAPI o'rganmoqdaman",
        "shahar": "Tashkent",
    }


# TODO (bonus): "/" endpointida qiziqarli fakt qaytaring
@app.get("/")
def fact():
  return {
    "fakt": "FastAPI nomi shundan kelib chiqqan — u haqiqatan ham 'tez' "
            "(fast), chunki Starlette va Pydantic tufayli Node.js va Go "
            "bilan bir qatorda turadigan performance ko'rsatadi."
  }