"""
Dars 03 — FastAPI Project yaratish
To'liq sozlangan FastAPI ilova namunasi.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Theater Manager API (demo)",
    description=(
        "Bu demo API — theater-manager loyihasiga o'xshab, "
        "spektakllar va aktyorlar haqida ma'lumot qaytaradi."
    ),
    version="0.1.0",
    contact={
        "name": "Uktam",
        "url": "https://github.com/OktamTurgun",
    },
)


@app.get("/", tags=["Root"])
def root():
    """Ildiz endpoint — API ishlab turganini tekshirish uchun."""
    return {"status": "ok", "message": "Theater Manager API ishlamoqda"}


@app.get("/health", tags=["Root"])
def health_check():
    """
    Health check endpoint — production'da monitoring tizimlar
    (masalan UptimeRobot, Render health check) shu manzilni chaqirib,
    server tirikligini tekshiradi.
    """
    return {"status": "healthy"}


@app.get("/performances", tags=["Performances"])
def list_performances():
    """Hozircha statik ro'yxat — Dars 15'da bu DB'dan keladi."""
    return {
        "performances": [
            {"id": 1, "title": "Alisa Mo'jizalar Mamlakatida"},
            {"id": 2, "title": "Pinokkio"},
        ]
    }


# Ishga tushirish:
# uvicorn main:app --reload
#
# Sinab ko'ring:
# http://127.0.0.1:8000/
# http://127.0.0.1:8000/health
# http://127.0.0.1:8000/performances
# http://127.0.0.1:8000/docs      <- Swagger, "tags" bo'yicha guruhlanganini ko'ring
# http://127.0.0.1:8000/redoc
# http://127.0.0.1:8000/openapi.json

## E'tibor bering: tags=["Root"] va tags=["Performances"] — bular
## /docs sahifasida endpointlarni guruhlarga ajratadi. Loyiha kattalashgan
## sayin bu guruhlash juda qulay bo'ladi.