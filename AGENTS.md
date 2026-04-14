# AGENTS.md

## Quick Start

```bash
uv sync                          # install deps (Python 3.12+, uses uv)
cp .env.example .env             # configure env vars (see gotchas below)
docker compose up -d             # start Postgres, MinIO, Neo4j, Redis, Airflow, SFTP
mkdir -p app/static              # REQUIRED — app fails without this (see gotchas)
alembic upgrade head              # run migrations
uvicorn app.main:api_service --reload
```

Run tests:
```bash
pytest                            # SQLite in-memory (pgvector tests auto-skipped)
TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/test_db" pytest  # full pgvector
```

Run a single test file or test:
```bash
pytest tests/unit/test_document_service.py
pytest tests/unit/test_document_service.py::test_function_name
```

Start a Celery worker:
```bash
celery -A app.worker.celery_app:celery_app worker --loglevel=INFO
```

## Architecture

- **Entry point**: `app/main.py:create_app()` → module-level `api_service`
- **Config**: `app/config/app_config.py` — Pydantic `BaseSettings` loaded from `.env`; `get_config()` is `@lru_cache`d
- **Database**: PostgreSQL + pgvector via SQLAlchemy (`app/config/db.py` + `app/models/`)
- **Migrations**: Alembic, config in `alembic.ini`, env reads `db.DATABASE_URL`
- **Dependency injection**: `app/api/deps.py` provides `DbSession`, `DocumentServiceDep`, `EmbeddingServiceDep`
- **Background tasks**: Celery with Redis broker (`app/worker/`)

### Active route modules (`app/api/routes/`)
`app.py`, `documents.py`, `jobs.py`, `chat.py`, `help.py`, `logs.py`, `users.py`

### Stale directory — do not add routes here
`app/routers/` exists (contains an empty `embeddings.py`) but is **not wired into the app**. All active routes are in `app/api/routes/`.

## Gotchas

### `app/static/` must exist or everything breaks
`main.py:34` does `StaticFiles(directory=static_path)` but `app/static/` is not in git. **Both `uvicorn` and `pytest` crash** with `RuntimeError: Directory does not exist`. Always run `mkdir -p app/static` after cloning.

### `.env.example` has dead `DB_*` variables
`AppConfig` uses `validation_alias` to read `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`, `POSTGRES_DB` from the environment. The `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`, `DB_NAME` vars in `.env.example` are **never read by the app**. Remove them or rename to match `POSTGRES_*`.

### Redis auth not in broker URL
`redis_url` builds `redis://host:port` without the password, but docker-compose Redis requires `--requirepass`. Celery broker/result connections will fail unless the URL includes auth. Fix: change `redis_url` to `f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"`.

### `db_name` defaults to `"rag"`, not `"grit"`
`AppConfig.db_name` has `validation_alias="POSTGRES_DB"` and Python default `"rag"`, but `.env.example` and docker-compose both use `"grit"`. If `POSTGRES_DB` is unset, the app connects to the wrong database.

### `get_config()` is cached
Uses `@lru_cache`. Changing env vars at runtime has no effect — restart the process.

### `JobStatus` is defined once, in models
`JobStatus` lives in `app/models/job.py` and is **imported** in `app/schemas/job.py`. Never duplicate the enum definition.

### Celery task dispatch pattern
- Use `celery_app.send_task(PROCESS_JOB_TASK_NAME, args=[...])` — **not** `.delay()`. Avoids circular imports and type-checker issues.
- The constant `PROCESS_JOB_TASK_NAME` in `celery_app.py` must match the task function name.
- Use `autoretry_for=(OperationalError,)` on the decorator, not manual try/except retry blocks.
- Tasks manage sessions via `SessionLocal()` with `try/finally: session.close()`, not `next(get_session())`.

### Docker init script runs once
`init-db.sh` only runs when the `postgres_data` volume is first created. To re-initialize: `docker compose down -v && docker compose up -d`, or manually create the `airflow` database and `vector` extension.

### Database driver
`DATABASE_URL` uses `postgresql+psycopg://` (driver: `psycopg`, not `psycopg2`).

### Apple Silicon
SFTP service uses `platform: linux/amd64` and requires Rosetta 2 (`softwareupdate --install-rosetta`).

## Test structure

- `tests/unit/` — unit tests (no DB needed)
- `tests/integration/` — integration tests (need `get_db` override, use SQLite by default)
- `@requires_pgvector` decorator (in `tests/conftest.py`) auto-skips when not on PostgreSQL with pgvector

## Code structure (active modules)

```
app/
├── api/
│   ├── deps.py              # FastAPI dependency injection
│   └── routes/              # route modules (app, documents, jobs, chat, help, logs, users)
├── config/
│   ├── app_config.py         # Pydantic settings (reads POSTGRES_* env vars)
│   └── db.py                 # SQLAlchemy engine + SessionLocal
├── core/                     # Logging and core utilities
├── embedding/                # Document loading, splitting, embedding pipeline
├── models/                   # SQLAlchemy models (base.py for shared DeclarativeBase)
├── repositories/             # Data access layer
├── schemas/                  # Pydantic request/response schemas
├── services/                  # Business logic (document.py, embedding.py)
├── templates/                 # Jinja2 HTML templates
└── worker/
    ├── celery_app.py          # Celery app + PROCESS_JOB_TASK_NAME constant
    ├── job_service.py
    └── tasks.py               # Celery tasks (process_documents)
```