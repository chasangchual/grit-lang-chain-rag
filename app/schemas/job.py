from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus


class JobCreate(BaseModel):
    name: str = Field(..., max_length=200, description="Job name")
    load_from: str = Field(..., max_length=500, description="Input directory path")


class FileResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str
    file_type: str
    parser_name: str
    processing_status: str
    content_length: int
    extracted_summary: str
    error_message: str | None
    created_at: datetime


class JobLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    level: str
    message: str
    created_at: datetime


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    input_dir: str
    status: JobStatus
    total_files: int
    processed_files: int
    celery_task_id: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class JobDetailResponse(JobResponse):
    logs: list[JobLogResponse] = Field(default_factory=list)
    results: list[FileResultResponse] = Field(default_factory=list)


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    skip: int
    limit: int
