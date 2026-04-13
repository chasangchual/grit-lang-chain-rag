from celery import Celery
from app.config.app_config import get_config

config = get_config()
PROCESS_JOB_TASK_NAME = "app.worker.tasks.process_document"

celery_app = Celery(
    "rag_embedding_pipeline",
    broker=config.celery_broker_url,
    backend=config.celery_result_backend,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_ack_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["app.worker.tasks"])
