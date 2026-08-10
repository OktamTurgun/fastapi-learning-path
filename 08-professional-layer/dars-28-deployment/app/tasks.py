import time
from app.celery_app import celery_app


@celery_app.task
def send_welcome_email(user_email: str) -> str:
    """Yangi foydalanuvchiga xush kelibsiz xabari yuborish (simulyatsiya)"""
    print(f"[Celery Worker] Xat yuborish boshlandi: {user_email}")
    time.sleep(3)  # Og'ir vazifa simulyatsiyasi
    print(f"[Celery Worker] Xat muvaffaqiyatli yuborildi: {user_email}")
    return f"Welcome email sent to {user_email}"
