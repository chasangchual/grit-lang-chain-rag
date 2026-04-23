from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.api.deps import DbSession
from app.models.job import DocumentsProcessJob, JobStatus
from app.schemas.job import (
    JobCreate,
    JobDetailResponse,
    JobListResponse,
    JobLogResponse,
    JobResponse,
    FileResultResponse,
)
from app.services.document_process_service import process_document_embedding
from app.worker.celery_app import celery_app, PROCESS_DOCS_TASK_NAME
from app.worker.tasks import handle_process_documents_job


router = APIRouter(prefix="/jobs", tags=["jobs"])


def job_to_response(job: DocumentsProcessJob) -> JobResponse:
    return JobResponse(
        id=job.id.value,
        name=job.name,
        input_dir=job.load_from,
        status=job.status,
        total_files=job.total_files,
        processed_files=job.processed_files,
        celery_task_id=job.celery_task_id,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new embedding job",
)
def create_job(
    schema: JobCreate,
    session: DbSession,
) -> JobResponse:
    from app.worker.job_service import create_job as create_job_record
    from app.config.db import SessionLocal, get_session

    job = create_job_record(session, name=schema.name, input_dir=schema.input_dir)

    # task = celery_app.send_task(PROCESS_DOCS_TASK_NAME, args=[job.id])
    # job.celery_task_id = task.id
    # session.commit()
    # return job_to_response(job)

    session = SessionLocal()
    process_document_embedding(SessionLocal(), job.input_dir)
    return job_to_response(job)

@router.get(
    "",
    response_model=JobListResponse,
    summary="List all jobs",
)
def list_jobs(
    session: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: JobStatus | None = Query(
        None, alias="status", description="Filter by status"
    ),
) -> JobListResponse:
    stmt = select(DocumentsProcessJob)
    if status_filter:
        stmt = stmt.where(DocumentsProcessJob.status == status_filter)
    stmt = stmt.order_by(DocumentsProcessJob.created_at.desc()).offset(skip).limit(limit)
    jobs = list(session.scalars(stmt).all())

    count_stmt = select(func.count()).select_from(DocumentsProcessJob)
    if status_filter:
        count_stmt = count_stmt.where(DocumentsProcessJob.status == status_filter)
    total = session.scalar(count_stmt) or 0

    return JobListResponse(
        items=[job_to_response(job) for job in jobs],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Get job details",
)
def get_job(
    job_id: int,
    session: DbSession,
) -> JobDetailResponse:
    from app.worker.job_service import get_job as get_job_record

    job = get_job_record(session, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    return JobDetailResponse(
        id=job.id,
        name=job.name,
        input_dir=job.input_dir,
        status=job.status,
        total_files=job.total_files,
        processed_files=job.processed_files,
        celery_task_id=job.celery_task_id,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        logs=[
            JobLogResponse(
                id=log.id,
                job_id=log.job_id,
                level=log.level,
                message=log.message,
                created_at=log.created_at,
            )
            for log in job.logs
        ],
        results=[FileResultResponse.model_validate(r) for r in job.results],
    )


@router.get(
    "/{job_id}/status",
    response_model=dict[str, Any],
    summary="Get Celery task status",
)
def get_task_status(job_id: int, session: DbSession) -> dict[str, Any]:
    job = session.get(DocumentsProcessJob, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    if not job.celery_task_id:
        return {"job_id": job_id, "status": job.status, "celery_status": None}

    task = AsyncResult(job.celery_task_id, app=celery_app)
    return {
        "job_id": job_id,
        "status": job.status,
        "celery_status": task.status,
        "celery_result": task.result if task.ready() else None,
    }
