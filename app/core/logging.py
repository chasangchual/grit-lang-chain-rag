
from __future__ import annotations

import json
import logging
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

from app.config.app_config import get_config

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
job_id_var: ContextVar[str | None] = ContextVar("job_id", default=None)
task_id_var: ContextVar[str | None] = ContextVar("task_id", default=None)
service_var: ContextVar[str | None] = ContextVar("service", default=None)

_configured_services: set[str] = set()
_record_factory_configured = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": getattr(record, "service", None),
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "job_id": getattr(record, "job_id", None),
            "task_id": getattr(record, "task_id", None),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


class ContextTextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        context_parts = []
        for key in ("service", "request_id", "job_id", "task_id"):
            value = getattr(record, key, None)
            if value:
                context_parts.append(f"{key}={value}")
        if context_parts:
            message = f"{message} {' '.join(context_parts)}"
        return message


class SizeAndTimeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(
        self,
        filename: str,
        *,
        max_bytes: int,
        backup_count: int,
    ) -> None:
        super().__init__(
            filename=filename,
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
            utc=True,
        )
        self.maxBytes = max_bytes

    def shouldRollover(self, record: logging.LogRecord) -> int:
        if super().shouldRollover(record):
            return 1

        if self.maxBytes <= 0:
            return 0

        if self.stream is None:
            self.stream = self._open()

        message = f"{self.format(record)}\n"
        self.stream.seek(0, 2)
        size_after_write = self.stream.tell() + len(message.encode(self.encoding or "utf-8", errors="replace"))
        return 1 if size_after_write >= self.maxBytes else 0


def _configure_record_factory() -> None:
    global _record_factory_configured
    if _record_factory_configured:
        return

    previous_factory = logging.getLogRecordFactory()

    def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = previous_factory(*args, **kwargs)
        record.request_id = request_id_var.get()
        record.job_id = job_id_var.get()
        record.task_id = task_id_var.get()
        record.service = service_var.get()
        return record

    logging.setLogRecordFactory(record_factory)
    _record_factory_configured = True


def configure_logging(service_name: str) -> None:
    _configure_record_factory()
    settings = get_config()
    if service_name in _configured_services:
        service_var.set(service_name)
        return

    settings.log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = Path(settings.log_dir) / f"{settings.log_file_basename}-{service_name}.log"
    formatter_name = "json" if settings.log_format.lower() == "json" else "text"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "job_runner.core.logging.JsonFormatter",
                },
                "text": {
                    "()": "job_runner.core.logging.ContextTextFormatter",
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": formatter_name,
                    "level": settings.log_level,
                },
                "file": {
                    "()": "job_runner.core.logging.SizeAndTimeRotatingFileHandler",
                    "formatter": formatter_name,
                    "level": settings.log_level,
                    "filename": str(log_file_path),
                    "max_bytes": settings.log_max_bytes,
                    "backup_count": settings.log_backup_count,
                },
            },
            "loggers": {
                "job_runner": {
                    "handlers": ["console", "file"],
                    "level": settings.log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console", "file"],
                    "level": settings.log_level,
                    "propagate": False,
                },
                "celery": {
                    "handlers": ["console", "file"],
                    "level": settings.log_level,
                    "propagate": False,
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": settings.log_level,
            },
        }
    )
    _configured_services.add(service_name)
    service_var.set(service_name)


def bind_log_context(
    *,
    request_id: str | None = None,
    job_id: str | None = None,
    task_id: str | None = None,
    service: str | None = None,
) -> dict[str, Token[str | None]]:
    tokens: dict[str, Token[str | None]] = {}
    if request_id is not None:
        tokens["request_id"] = request_id_var.set(request_id)
    if job_id is not None:
        tokens["job_id"] = job_id_var.set(job_id)
    if task_id is not None:
        tokens["task_id"] = task_id_var.set(task_id)
    if service is not None:
        tokens["service"] = service_var.set(service)
    return tokens


def reset_log_context(tokens: dict[str, Token[str | None]]) -> None:
    if "request_id" in tokens:
        request_id_var.reset(tokens["request_id"])
    if "job_id" in tokens:
        job_id_var.reset(tokens["job_id"])
    if "task_id" in tokens:
        task_id_var.reset(tokens["task_id"])
    if "service" in tokens:
        service_var.reset(tokens["service"])


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
