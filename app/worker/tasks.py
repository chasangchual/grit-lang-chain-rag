from __future__ import annotations

from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.exc import OperationalError

from app.config.db import SessionLocal
from app.worker.celery_app import celery_app


@celery_app.task(name="app.worker.tasks.add")
def add(x, y):
    return x + y


@celery_app.task(
    bind=True,
    name="app.worker.tasks.process_documents",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def process_documents(self, job_id: int):
    from app.worker.job_service import (
        get_job,
        mark_job_running,
        mark_job_failed,
        mark_job_completed,
    )

    session = SessionLocal()
    job = None
    try:
        job = get_job(session, job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        mark_job_running(session, job, total_files=0, celery_task_id=self.request.id)

        # TODO: actual document processing logic here
        mark_job_completed(session, job)

    except MaxRetriesExceededError:
        if job:
            mark_job_failed(session, job, error_message="Max retries exceeded")
        raise
    except Exception as e:
        if job:
            if not isinstance(e, OperationalError):
                mark_job_failed(session, job, error_message=str(e))
            else:
                # OperationalError will be auto-retried by autoretry_for
                mark_job_failed(session, job, error_message=f"Retrying: {e}")
        raise
    finally:
        session.close()
