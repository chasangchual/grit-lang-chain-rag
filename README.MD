# Grit Local Infrastructure (Data Pipeline Stack)

This repository provisions a local infrastructure stack for development and testing.

It includes:
- **PostgreSQL 16 + pgvector** (application database, vector search, and Airflow metadata)
- **Apache Airflow 2.8.1** using **LocalExecutor**
- **Airflow init service** to bootstrap the metadata DB and create an admin user
- **MinIO** (S3-compatible object storage)
- **Neo4j 5** (graph database)
- **Redis 7** (kept for another local project; Airflow does **not** require it in this setup)
- **Alpine SFTP** (source data simulation)
- **Docker Mailserver** (email testing)

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
- `airflow-init`
- `airflow-webserver`
- `airflow-scheduler`
- `sftp`
- `mailserver`

Airflow uses:
- `AIRFLOW__CORE__EXECUTOR=LocalExecutor`
- PostgreSQL for metadata
- no Celery worker
- `airflow-init` to run `airflow db migrate` and create an admin user before the webserver and scheduler start

### init-db.sh
This script:
- creates the `airflow` database
- enables `vector` in `${POSTGRES_DB}`
- enables `vector` in `airflow`

### .env
Create `.env` by copying `.env.example` and replacing sample values.

To generate `AIRFLOW_FERNET_KEY`:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 3. Example .env

```dotenv
# Postgres
POSTGRES_DB=grit
POSTGRES_USER=grit-admin
POSTGRES_PASSWORD=password123

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Neo4j
NEO4J_DATABASE=neo4j
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Redis
REDIS_PORT=6379

# SFTP
SFTP_USER=grituser
SFTP_PASS=gritpass

# Email
MAIL_DOMAIN=example.com

# Airflow
AIRFLOW_FERNET_KEY=YOUR_GENERATED_KEY_HERE
AIRFLOW_UID=50000
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin
AIRFLOW_ADMIN_FIRSTNAME=Admin
AIRFLOW_ADMIN_LASTNAME=User
AIRFLOW_ADMIN_EMAIL=admin@example.com
```

---

## 4. Initialization

Create local directories and make the database init script executable:

```bash
mkdir -p ./airflow/dags ./airflow/logs ./airflow/plugins ./sftp_upload
chmod -R 777 ./airflow
chmod +x init-db.sh
```

> Note: PostgreSQL init scripts in `/docker-entrypoint-initdb.d` run only when the database directory is empty. If `postgres_data` already exists, `init-db.sh` will not run again automatically.

If this is a fresh start and you want a clean bootstrap:

```bash
docker compose down -v
docker compose up -d
```

On startup, `airflow-init` will:
- wait for Postgres to be healthy
- run `airflow db migrate`
- create the Airflow admin user
- allow the webserver and scheduler to start afterward

---

## 5. How to run

Start all services:

```bash
docker compose up -d
```

Check status:

```bash
docker compose ps
```

Check Airflow init logs:

```bash
docker compose logs airflow-init
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
- **Airflow UI:** `http://localhost:8080`
- **SFTP:** `localhost:2222`
- **SMTP:** `localhost:25`
- **Mail submission:** `localhost:587`

Default Airflow admin credentials come from `.env`:
- username: `${AIRFLOW_ADMIN_USERNAME}`
- password: `${AIRFLOW_ADMIN_PASSWORD}`

---

## 7. How to verify

### Verify containers

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