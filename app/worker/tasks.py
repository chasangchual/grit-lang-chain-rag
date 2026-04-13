from __future__ import annotations
from pathlib import Path 
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config.app_config import get_config
from app.config.db import get_session
from app.worker.celery_app import celery_app

@celery_app.task
def add(x, y):
    return x + y

@celery_app.task
def process_documents(job_id: int):
    from app.worker.job_service import get_job, mark_job_running, mark_job_retrying
    session = next(get_session())
    job = get_job(session, job_id)
    if not job:
        raise ValueError(f"Job with id {job_id} not found")
    
    try:
        # Simulate processing documents
        total_files = 10  # This would be determined by counting files in the input directory
        mark_job_running(session, job, total_files=total_files, celery_task_id=process_documents.request.id)
        
        for i in range(total_files):
            # Simulate processing each file
            pass
        
        # Mark job as completed (this would be done in the actual implementation)
        # mark_job_completed(session, job)
        
    except OperationalError as e:
        try:
            mark_job_retrying(session, job, error_message=str(e))
            raise retry(exc=e, countdown=60)  # Retry after 60 seconds
        except MaxRetriesExceededError:
            mark_job_retrying(session, job, error_message="Max retries exceeded")