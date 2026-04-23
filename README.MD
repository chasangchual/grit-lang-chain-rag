# Grit Local Infrastructure (Data Pipeline Stack)

This repository provisions a local infrastructure stack for development and testing.

It includes:
- **PostgreSQL 16 + pgvector** (application database, vector search, and Airflow metadata)
- **MinIO** (S3-compatible object storage)
- **Neo4j 5** (graph database)
- **Redis 7** (kept for another local project; Airflow does **not** require it in this setup)

In this version, **`celery-worker` and `celery-flower` are removed** because Airflow is configured with `LocalExecutor`.

---

## 1. Prerequisites

- **Docker Engine / Docker Desktop**
- **Docker Compose v2**
- **System Memory:** minimum 4 GB, 8 GB+ recommended
- **Mac users (Apple Silicon):** install **Rosetta 2** if needed because the SFTP service uses `linux/amd64`

```bash
softwareupdate --install-rosetta
```

### Install PostgreSQL client

If you only need to connect to remote databases and do not want to run a local PostgreSQL server, you should install libpq. 

**Update Homebrew:**
Ensure your package definitions are up to date by running:
```bash
brew update
```
**Install libpq:**
This package contains the PostgreSQL client tools without the full server.
```bash
brew install libpq
```
**Link the binaries:**
libpq is "keg-only," meaning it is not automatically added to your system path. You must force-link it or add it to your shell configuration to use psql.
```bash
brew link --force libpq
```
Note: If linking fails, you may need to add the path to your .zshrc or .bash_profile as instructed in the Homebrew "Caveats" output. 


---

## 2. Files

Place these files in your project root:
- `docker-compose.yml`
- `init-db.sh`
- `.env` (copy from `.env.example`)
- `.env.example`

### docker-compose.yml
This compose file starts:
- `postgres`
- `minio`
- `neo4j`
- `redis`


### init-db.sh
This script:
- creates the `airflow` database
- enables `vector` in `${POSTGRES_DB}`

### .env
Create `.env` by copying `.env.example` and replacing sample values.

---

## 3. Example .env

```dotenv
# Database Connection (for application)
DB_USER=grit-admin
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=grit

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Neo4j
NEO4J_DATABASE=neo4j
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Redis
REDIS_PORT=6379

```

---

## 4. Initialization


---

### Database schema migration

Run the `alembic init migration` command in the project root whree pyproject.toml exists 
refer, https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration and https://alembic.sqlalchemy.org/en/latest/tutorial.html

```
$> alembic init migration 

  Creating directory <project root>/migrations ...  done
  Creating directory <project root>/migrations/versions ...  done
  Generating <project root>/migrations/script.py.mako ...  done
  Generating <project root>/migrations/env.py ...  done
  Generating <project root>/migrations/README ...  done
  Generating <project root>/alembic.ini ...  done
  ```

### Core Migration Commands
- **Apply all migrations**: Update your database to the most recent version.
```bash
alembic upgrade head
```
> Note: head refers to the latest revision in your Alembic versions directory.

- **Revert the last migration**: Roll back the database schema by exactly one version.
```bash
alembic downgrade -1
```
*Alternatively*, you can downgrade to a specific version by using its unique Revision ID.

- **Check current status**: View which migration version is currently applied to your database.
```bash
alembic current
```
> This command queries the `alembic_version` table in your database to find the active Revision ID. 


### Create a Migration Script 
With the environment in place we can create a new revision, using alembic revision:
```
alembic revision  --autogenerate  -m "create account table"
```

## 5. How to run

Start all infrastructure services:

```bash
docker compose up -d
```

Start the FastAPI application:

```bash
uvicorn app.main:api_service --reload
```

Start the Celery worker (in a **separate terminal**):

```bash
celery -A app.worker.celery_app:celery_app worker --loglevel=INFO
```

> The Celery worker must be running for background jobs (document processing) to execute. Without it, tasks are enqueued in Redis but never consumed.

### Trigger a Celery task manually

From the Celery CLI:

```bash
# Quick test with the built-in add task
celery -A app.worker.celery_app:celery_app call app.worker.tasks.add --args='[1,2]'

# Trigger document processing for a specific job ID
celery -A app.worker.celery_app:celery_app call app.worker.tasks.process_documents --args='[1]'
```

From a Python shell:

```python
from app.worker.celery_app import celery_app

# Using send_task (no task import needed)
celery_app.send_task("app.worker.tasks.process_documents", args=[1])

# Or import and call directly
from app.worker.tasks import process_documents
process_documents.delay(1)
```

> Ensure the Celery worker is running before triggering tasks, or they will remain queued in Redis unprocessed.

Check status:

```bash
docker compose ps
```

Stop services:

```bash
docker compose down
```

Stop services and remove volumes:

```bash
docker compose down -v
```

---

## 6. What you get

After startup, these endpoints are available:

- **Postgres:** `localhost:5432`
- **MinIO API:** `http://localhost:9000`
- **MinIO Console:** `http://localhost:9001`
- **Neo4j Browser:** `http://localhost:7474`
- **Neo4j Bolt:** `localhost:7687`
- **Redis:** `localhost:6379`


---

## 7. How to verify

### Verify containers

- install PostgreSQL client
```bash
brew install libpq
```

```bash
docker compose ps
```

### Verify Postgres databases

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d postgres -c "\l"
```

You should see both your main database (for example `grit`) and `airflow`.

### Verify pgvector

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT extname FROM pg_extension WHERE extname='vector';"
docker compose exec postgres psql -U "$POSTGRES_USER" -d airflow -c "SELECT extname FROM pg_extension WHERE extname='vector';"
```

### Verify Airflow init

```bash
docker compose logs airflow-init
```

You should see successful output from `airflow db migrate`.

### Verify Airflow web UI
Open `http://localhost:8080`

### Verify Redis

```bash
docker compose exec redis redis-cli ping
```

Expected result:

```text
PONG
```

### Verify MinIO
Open `http://localhost:9001` and sign in with values from `.env`.

### Verify Neo4j
Open `http://localhost:7474` and sign in with values from `.env`.

---

## 8. Troubleshooting

### Problem: `airflow` database does not exist

This usually means `postgres_data` already existed, so `init-db.sh` did not run again.

#### Manual recovery steps (without deleting volumes)

Run the following commands:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE airflow;"
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker compose exec postgres psql -U "$POSTGRES_USER" -d airflow -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker compose run --rm airflow-init
```

That will:
- create the `airflow` database
- enable `vector` in both databases
- rerun Airflow metadata initialization and admin-user creation

#### Clean reset option

```bash
docker compose down -v
docker compose up -d
```

Use this when you are fine removing existing local Postgres data.

### Problem: Airflow UI is up but login fails

Check the value of these variables in `.env`:

```dotenv
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin
```

If needed, recreate the user:

```bash
docker compose run --rm airflow-init
```

### Problem: `airflow-init` finished before you checked it

This is normal. It is a one-time bootstrap container. View its logs with:

```bash
docker compose logs airflow-init
```

# Getting Started

Follow the steps below to initialize the project and install dependencies using `uv`.

## 1. Initialize the Project

Initialize the project environment. This will create the necessary project configuration and environment files if they do not already exist.

**Description**
* Sets up the project structure for uv
* Creates or validates the pyproject.toml
* Prepares the environment for dependency management


```bash
uv init
```

## 2. Install and Sync Dependencies
Install all dependencies defined in pyproject.toml and synchronize the environment.

```bash
uv sync
```

**Description**
* Creates the virtual environment (if not already created)
* Installs dependencies listed in pyproject.toml
* Ensures the environment matches the lock file (uv.lock) if present
