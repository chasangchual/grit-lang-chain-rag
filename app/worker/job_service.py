from __future__ import annotations

from pathlib import Path
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config.app_config import get_config
from app.models.job import FileResult, DocumentsProcessJob, DocumentsProcess, JobStatus

logger = logging.getLogger("job_runner.jobs")


def create_job(session: Session, name: str, load_from: str) -> DocumentsProcessJob:
    config = get_config()
    resolved_dir = str(Path(load_from))
    job = DocumentsProcessJob(name=name, input_dir=resolved_dir)
    session.add(job)
    session.commit()
    session.refresh(job)
    add_job_log(session, job.id.value, f"Job created for input directory: {resolved_dir}")
    return job


def add_job_log(session: Session, job_id: int, message: str, level: str = "INFO") -> None:
    session.add(DocumentsProcess(job_id=job_id, message=message, level=level))
    session.commit()
    getattr(logger, level.lower(), logger.info)("job_id=%s %s", job_id, message)


def get_job(session: Session, job_id: int) -> DocumentsProcessJob | None:
    stmt = (
        select(DocumentsProcessJob)
        .where(DocumentsProcessJob.id == job_id)
        .options(selectinload(DocumentsProcessJob.logs), selectinload(DocumentsProcessJob.results))
    )
    return session.scalar(stmt)


def list_jobs(session: Session) -> list[DocumentsProcessJob]:
    stmt = select(DocumentsProcessJob).order_by(DocumentsProcessJob.created_at.desc())
    return list(session.scalars(stmt).all())


def mark_job_running(session: Session, job: DocumentsProcessJob, total_files: int, celery_task_id: str) -> None:
    from datetime import datetime, timezone

    job.status = JobStatus.running
    job.total_files = total_files
    job.celery_task_id = celery_task_id
    job.started_at = datetime.now(timezone.utc)
    session.commit()


def mark_job_retrying(session: Session, job: DocumentsProcessJob, error_message: str) -> None:
    job.status = JobStatus.retrying
    job.error_message = error_message
    session.commit()


def increment_processed_files(session: Session, job: DocumentsProcessJob) -> None:
    job.processed_files += 1
    session.commit()


def store_file_result(session: Session, job_id: int, result: dict[str, str | int | None]) -> None:
    existing = session.scalar(
        select(FileResult).where(
            FileResult.job_id == job_id,
            FileResult.file_path == str(result["file_path"]),
        )
    )
    if existing:
        for field, value in result.items():
            setattr(existing, field, value)
    else:
        session.add(FileResult(job_id=job_id, **result))
    session.commit()


def mark_job_completed(session: Session, job: DocumentsProcessJob) -> None:
    from datetime import datetime, timezone

    job.status = JobStatus.completed
    job.finished_at = datetime.now(timezone.utc)
    session.commit()


def mark_job_failed(session: Session, job: DocumentsProcessJob, error_message: str) -> None:
    from datetime import datetime, timezone

    job.status = JobStatus.failed
    job.error_message = error_message
    job.finished_at = datetime.now(timezone.utc)
    session.commit()
