# Grit Local Infrastructure (Docker Compose)

This repository contains a `docker-compose.yml` that provisions a
complete local infrastructure stack for development and testing.

It includes:

-   PostgreSQL 16 (Relational Database)
-   MinIO (S3-compatible Object Storage)
-   Neo4j 5 (Graph Database)
-   Redis 7 (In-memory Cache / KV Store)

All services run locally using Docker and persist data via named
volumes.

------------------------------------------------------------------------

# Architecture Overview

  Service    Container Name   Ports                   Purpose
  ---------- ---------------- ----------------------- ------------------
  Postgres   grit-postgres    5432                    Relational DB
  MinIO      grit-minio       9000 (API), 9001 (UI)   Object storage
  Neo4j      grit-neo4j       7474 (UI), 7687         Graph DB
  Redis      grit-redis       6379                    Cache / KV store

Persistent Volumes: - postgres_data - minio_data - neo4j_data -
neo4j_logs - redis_data

------------------------------------------------------------------------

# Prerequisites

-   Docker Engine / Docker Desktop
-   Docker Compose v2

Verify:

    docker --version
    docker compose version

------------------------------------------------------------------------

# Environment Variables (.env Required)

This project requires a `.env` file before starting the stack.

## Step 1: Copy template

    cp .env.example .env

## Step 2: Update values

Edit `.env` and replace all `CHANGE_ME_*` values with secure
credentials.

### Postgres

-   POSTGRES_DB
-   POSTGRES_USER
-   POSTGRES_PASSWORD

Used during container initialization and healthcheck.

### Neo4j

-   NEO4J_DATABASE
-   NEO4J_USER
-   NEO4J_PASSWORD

Docker Compose combines these as:

    NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}

### MinIO

-   MINIO_ROOT_USER
-   MINIO_ROOT_PASSWORD

Used for MinIO Console login (http://localhost:9001) and S3 API
(http://localhost:9000).

### Redis

-   REDIS_PORT
-   REDIS_PASSWORD

Note: Current docker-compose does NOT enforce Redis AUTH by default.

------------------------------------------------------------------------

# How to Run

Start services:

    docker compose up -d

Check status:

    docker compose ps

View logs:

    docker compose logs -f

Stop services:

    docker compose down

Remove volumes (delete data):

    docker compose down -v

------------------------------------------------------------------------

# Verification

Check containers:

    docker ps

Postgres test:

    docker exec -it grit-postgres psql -U grit-admin -d grit -c "SELECT 1;"

Redis test:

    docker exec -it grit-redis redis-cli ping

Expected:

    PONG

MinIO health:

    curl http://localhost:9000/minio/health/live

Neo4j UI:

    http://localhost:7474

------------------------------------------------------------------------

# Security Notes

-   `.env` contains secrets --- do NOT commit it.
-   `.env.example` is safe to commit.
-   Restart containers after updating credentials.
