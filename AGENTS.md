# AGENTS.md

## Project Overview

FastAPI application for RAG (Retrieval-Augmented Generation) using LangChain, PostgreSQL with pgvector, and Celery for async processing.

## Prerequisites

- **Python**: 3.12+ (see `.python-version`)
- **uv**: Python package manager (`brew install uv` or `pip install uv`)
- **Docker**: For local infrastructure services

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Start infrastructure**:
   ```bash
   docker compose up -d
   ./check_services.sh  # Verify all services are healthy
   ```

4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

## Running the Application

```bash
uvicorn app.main:api_service --reload
```

## Database Migrations

- `alembic upgrade head` - Apply all migrations
- `alembic downgrade -1` - Rollback one migration
- `alembic current` - Check current version
- `alembic revision -m "description"` - Create new migration

## Testing

Tests use **SQLite in-memory database by default** (no pgvector). Vector search tests are automatically skipped with SQLite.

Run tests:
```bash
pytest
```

Run with PostgreSQL (full pgvector support):
```bash
TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/test_db" pytest
```

Tests requiring pgvector use the `@requires_pgvector` decorator (see `tests/conftest.py`).

## Architecture

- **Entry point**: `app/main.py:create_app()` → `api_service`
- **Config**: `app/config/app_config.py` - Pydantic settings loaded from `.env`
- **Database**: PostgreSQL with pgvector (`app/config/db.py` + `app/models/`)
- **Migrations**: Alembic config in `alembic.ini`, env reads `db.DATABASE_URL`
- **Background tasks**: Celery with Redis broker (`app/worker/`)

## Key Gotchas

1. **Config caching**: `get_config()` is cached with `@lru_cache`. If you modify environment variables during runtime, restart the process or clear the cache.

2. **Docker init script**: `init-db.sh` only runs once when the `postgres_data` volume is created. To re-initialize:
   ```bash
   docker compose down -v  # Removes volumes
   docker compose up -d
   ```
   Or manually create the `airflow` database and `vector` extension (see README).

3. **Database URL construction**: `DATABASE_URL` is built in `AppConfig.database_url` as `postgresql+psycopg://...` (note the driver: `psycopg`, not `psycopg2`).

4. **Redis auth**: Redis requires password (set `REDIS_PASSWORD` in `.env`).

5. **Mac (Apple Silicon)**: SFTP service uses `platform: linux/amd64` and requires Rosetta 2.

## Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| Postgres | 5432 | Main DB + pgvector |
| MinIO API/Console | 9000/9001 | S3-compatible storage |
| Neo4j Browser/Bolt | 7474/7687 | Graph database |
| Redis | 6379 | Celery broker |
| Airflow Web UI | 8080 | Workflow orchestration |
| SFTP | 2222 | File upload |

## Code Structure

```
app/
├── api/routes/      # FastAPI route handlers
├── config/          # App configuration + DB setup
├── core/            # Logging and core utilities
├── embedding/       # Document loading, splitting, embedding pipeline
├── models/          # SQLAlchemy models (base.py for shared timestamp mixin)
├── repositories/    # Data access layer
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic layer
├── templates/       # Jinja2 HTML templates
└── worker/          # Celery tasks
```