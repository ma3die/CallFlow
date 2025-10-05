from celery import Celery

from src.core.celery_config import celery_

celery_app = Celery(**celery_.model_dump())

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)

celery_app.autodiscover_tasks()
