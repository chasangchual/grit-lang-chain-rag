from __future__ import annotations

from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.exc import OperationalError

from app.config.db import SessionLocal, get_session
from app.models.job import DocumentsProcessJob
from app.worker.celery_app import celery_app, PROCESS_DOCS_TASK_NAME
from app.worker.job_service import get_job
from app.services.document_process_service import process_document

@celery_app.task(name="app.worker.tasks.add")
def add(x, y):
    return x + y


@celery_app.task(
    bind=True,
    name=PROCESS_DOCS_TASK_NAME,
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def handle_process_documents_job(self, job_id: int):
    print(f'''Processing documents for job_id: {job_id}''')
    
    session = SessionLocal()
    try:
        job = get_job(session, job_id)
        if job:
            return process_document(session, job, self.request.id)
        else:
            raise ValueError(f"Job with id {job_id} not found")
    finally:
        session.close()

