from __future__ import annotations

from pathlib import Path
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config.config import get_config
from app.models.job import FileResult, Job, JobLog, JobStatus

logger = logging.getLogger("job_runner.jobs")


def create_job(session: Session, name: str, input_dir: str | None) -> Job:
    config = get_config()
    resolved_dir = str(Path(input_dir) if input_dir else config.job_input_dir)
    job = Job(name=name, input_dir=resolved_dir)
    session.add(job)
    session.commit()
    session.refresh(job)
    add_job_log(session, job.id, f"Job created for input directory: {resolved_dir}")
    return job


def add_job_log(session: Session, job_id: int, message: str, level: str = "INFO") -> None:
    session.add(JobLog(job_id=job_id, message=message, level=level))
    session.commit()
    getattr(logger, level.lower(), logger.info)("job_id=%s %s", job_id, message)


def get_job(session: Session, job_id: int) -> Job | None:
    stmt = (
        select(Job)
        .where(Job.id == job_id)
        .options(selectinload(Job.logs), selectinload(Job.results))
    )
    return session.scalar(stmt)


def list_jobs(session: Session) -> list[Job]:
    stmt = select(Job).order_by(Job.created_at.desc())
    return list(session.scalars(stmt).all())


def mark_job_running(session: Session, job: Job, total_files: int, celery_task_id: str) -> None:
    from datetime import datetime, timezone

    job.status = JobStatus.running
    job.total_files = total_files
    job.celery_task_id = celery_task_id
    job.started_at = datetime.now(timezone.utc)
    session.commit()


def mark_job_retrying(session: Session, job: Job, error_message: str) -> None:
    job.status = JobStatus.retrying
    job.error_message = error_message
    session.commit()


def increment_processed_files(session: Session, job: Job) -> None:
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


def mark_job_completed(session: Session, job: Job) -> None:
    from datetime import datetime, timezone

    job.status = JobStatus.completed
    job.finished_at = datetime.now(timezone.utc)
    session.commit()


def mark_job_failed(session: Session, job: Job, error_message: str) -> None:
    from datetime import datetime, timezone

    job.status = JobStatus.failed
    job.error_message = error_message
    job.finished_at = datetime.now(timezone.utc)
    session.commit()
