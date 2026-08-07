from app.celery_app import celery_app
import time


@celery_app.task(name="send_order_confirmation_sms")
def send_order_confirmation_sms(
    customer_phone: str,
    customer_name: str,
    order_id: int,
    total_amount: float,
):
    """
    Buyurtma yaratilganda mijozga tasdiqlovchi SMS yuborish — fon
    vazifa sifatida. Hozircha haqiqiy SMS-gateway ulanish yo'q, faqat
    2 soniyalik kutish orqali "sekin tashqi so'rov"ni simulyatsiya
    qilamiz.
    """
    time.sleep(2)
    print(
        f"[Celery] SMS yuborildi: {customer_phone} ({customer_name}) — "
        f"buyurtma #{order_id}, summa: {total_amount} so'm"
    )
    return {
        "status": "sent",
        "phone": customer_phone,
        "order_id": order_id,
    }