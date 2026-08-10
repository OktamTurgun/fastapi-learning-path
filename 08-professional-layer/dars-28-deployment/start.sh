#!/bin/sh
set -e

echo "=== [PRODUCTION STARTUP] ==="
echo "1. Ma'lumotlar bazasi migratsiyasini yurgizish (Alembic)..."
alembic upgrade head

echo "2. Gunicorn serverini Uvicorn workerlari bilan ishga tushirish..."
# 4 ta worker jarayoni multi-core CPU unumdorligini oshiradi
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
