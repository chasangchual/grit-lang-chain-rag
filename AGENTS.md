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

Check infrastructure health:
```bash
bash check_services.sh            # checks Docker containers are running/healthy
```

## Architecture

- **Entry point**: `app/main.py:create_app()` → module-level `api_service`
- **Config**: `app/config/app_config.py` — Pydantic `BaseSettings` loaded from `.env`; `get_config()` is `@lru_cache`d
- **Database**: PostgreSQL + pgvector via SQLAlchemy (`app/config/db.py` + `app/models/`)
- **Migrations**: Alembic, config in `alembic.ini`, `migrations/env.py` reads `db.DATABASE_URL`
- **Dependency injection**: `app/api/deps.py` provides `DbSession`, `DocumentServiceDep`, `EmbeddingServiceDep`
- **Background tasks**: Celery with Redis broker (`app/worker/`)

### Active route modules (`app/api/routes/`)
`app.py`, `documents.py`, `jobs.py`, `chat.py`, `help.py`, `logs.py`, `users.py`

### Stale directory — do not add routes here
`app/routers/` exists (contains an empty `embeddings.py`) but is **not wired into the app**. All active routes are in `app/api/routes/`.

## Gotchas

### `app/static/` must exist or everything breaks
`main.py:33-34` does `StaticFiles(directory=static_path)` but `app/static/` is not in git. **Both `uvicorn` and `pytest` crash** with `RuntimeError: Directory does not exist`. Always run `mkdir -p app/static` after cloning.

### `.env.example` has dead `DB_*` variables
`AppConfig` uses `validation_alias` to read `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`, `POSTGRES_DB` from the environment. The `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`, `DB_NAME` vars in `.env.example` are **never read by the app**. Remove them or rename to match `POSTGRES_*`.

### `.env.example` is missing `POSTGRES_HOST`
`AppConfig.db_host` reads `POSTGRES_HOST` via `validation_alias`, defaulting to `localhost`. If you need a non-local Postgres, set `POSTGRES_HOST` explicitly.

### `db_name` defaults to `"rag"`, not `"grit"`
`AppConfig.db_name` has `validation_alias="POSTGRES_DB"` and Python default `"rag"`, but `.env.example` and docker-compose both use `"grit"`. If `POSTGRES_DB` is unset, the app connects to the wrong database.

### `get_config()` is cached
Uses `@lru_cache`. Changing env vars at runtime has no effect — restart the process.

### Module-level config and engine in `db.py`
`db.py` runs `config = get_config()` and `engine = create_engine(DATABASE_URL)` at import time. This means tests cannot override the database URL after import — the test conftest creates its own engine instead.

### `LocalDocumentsProcessJob` import is broken
Multiple files import `LocalDocumentsProcessJob` from `app.models.job`, but the model class is actually named `DocumentsProcessJob`. This will cause `ImportError` at runtime. Either rename the class or add an alias.

### `config.job_input_dir` does not exist
`app/worker/job_service.py:17` references `config.job_input_dir` but `AppConfig` has no such field. This will raise `AttributeError` at runtime. The working directory config field is `working_directory` (defaults to `/app/data`).

### `JobStatus` is defined once, in models
`JobStatus` lives in `app/models/job.py` and is **imported** in `app/schemas/job.py`. Never duplicate the enum definition.

### Celery task dispatch pattern
- The task name constant is `PROCESS_DOCS_TASK_NAME` (not `PROCESS_JOB_TASK_NAME`).
- Use `celery_app.send_task(PROCESS_DOCS_TASK_NAME, args=[...])` — **not** `.delay()`. Avoids circular imports.
- The task function name is `handle_process_documents_job`; the registered task name string is `"app.worker.tasks.process_documents"`.
- Use `autoretry_for=(OperationalError,)` on the decorator for new tasks, not manual try/except retry blocks.
- Tasks manage sessions via `SessionLocal()` with `try/finally: session.close()`, not `next(get_session())`.

### `migrations/env.py` has a spurious import
`from sympy import im` on line 7 is unused and will cause `ImportError` if `sympy` is not installed. Remove it.

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
- No lint, typecheck, or formatter commands are configured — none to run

## Code structure (active modules)

```
app/
├── api/
│   ├── deps.py              # FastAPI dependency injection
│   └── routes/              # route modules (app, documents, jobs, chat, help, logs, users)
├── config/
│   ├── app_config.py         # Pydantic settings (reads POSTGRES_* env vars)
│   └── db.py                 # SQLAlchemy engine + SessionLocal (module-level config)
├── core/                     # Logging and core utilities
├── embedding/                # Document loading, splitting, embedding pipeline
├── models/                   # SQLAlchemy models (base.py for shared DeclarativeBase)
├── repositories/             # Data access layer
├── schemas/                  # Pydantic request/response schemas
├── services/                  # Business logic (document.py, document_process_service.py, embedding.py)
├── templates/                 # Jinja2 HTML templates
└── worker/
    ├── celery_app.py          # Celery app + PROCESS_DOCS_TASK_NAME constant
    ├── job_service.py
    └── tasks.py               # Celery tasks (handle_process_documents_job)
```