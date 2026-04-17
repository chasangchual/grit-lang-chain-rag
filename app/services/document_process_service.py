from math import log
import uuid

from sqlalchemy.orm import Session
import logging

from app.config.db import SessionLocal
from app.models.job import Job
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.exc import OperationalError
from app.worker.job_service import (
    get_job,
    mark_job_running,
    mark_job_failed,
    mark_job_completed,
)


def process_document(session: Session, job: Job, task_id: str | None):
    print(f"""Processing documents for job_id: {job.id}""")

    try:
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        mark_job_running(
            session, job, total_files=0, celery_task_id=task_id or str(uuid.uuid4())
        )

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
        logging.info(f"Finished processing job_id: {job.id if job else 'unknown'}")
