from app.celery_app import celery_app
import time


@celery_app.task(name="send_confirmation_email")
def send_confirmation_email(email: str, order_id: int):
    """
    Buyurtma tasdiqlanganda mijozga email yuborish — fon vazifa sifatida.
    Hozircha haqiqiy SMTP ulanish yo'q, faqat 2 soniyalik kutish orqali
    "sekin tashqi so'rov"ni simulyatsiya qilamiz.
    """
    time.sleep(2)
    print(f"[Celery] Email yuborildi: {email}, buyurtma #{order_id}")
    return {"status": "sent", "email": email, "order_id": order_id}

@celery_app.task(name="notify_new_product")
def notify_new_product(product_name: str, product_id: int):
    """
    Yangi mahsulot qo'shilganda administratorlarga bildirishnoma
    yuborish — fon vazifa sifatida (masalan email yoki Telegram orqali,
    hozircha simulyatsiya).
    """
    time.sleep(2)
    print(f"[Celery] Bildirishnoma: yangi mahsulot qo'shildi — {product_name} (ID: {product_id})")
    return {"status": "notified", "product_id": product_id}