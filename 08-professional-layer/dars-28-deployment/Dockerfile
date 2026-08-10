# Production Dockerfile for FastAPI
FROM python:3.13-slim

# Python optimizatsiyalari (pyc fayllar yozmaslik, stdout buferlamaslik)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Xavfsizlik uchun root bo'lmagan foydalanuvchi yaratish
RUN addgroup --system appuser && adduser --system --group appuser

# Bog'liqliklarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Manba kodini nusxalash
COPY . $APP_HOME

# Skriptga ijro huquqini berish va egasini o'zgartirish
RUN chmod +x ./start.sh && chown -R appuser:appuser $APP_HOME

USER appuser

EXPOSE 8000

CMD ["./start.sh"]
