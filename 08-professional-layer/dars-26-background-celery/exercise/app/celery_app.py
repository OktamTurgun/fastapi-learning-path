from celery import Celery

celery_app = Celery(
    "storely",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks"],   # <- YANGI: qaysi modulda tasklar borligini aytadi
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tashkent",
)