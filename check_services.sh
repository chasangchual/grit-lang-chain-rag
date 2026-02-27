#!/bin/bash

set -e

SERVICES=(
  grit-postgres
  grit-minio
  grit-neo4j
  grit-redis
)

FAILED=0

for SERVICE in "${SERVICES[@]}"; do
  echo "Checking $SERVICE..."

  if ! docker ps --format '{{.Names}}' | grep -q "^${SERVICE}$"; then
    echo "❌ $SERVICE is NOT running"
    FAILED=1
    continue
  fi

  HEALTH=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' $SERVICE)

  if [ "$HEALTH" == "healthy" ] || [ "$HEALTH" == "no-healthcheck" ]; then
    echo "✅ $SERVICE is running ($HEALTH)"
  else
    echo "❌ $SERVICE is unhealthy ($HEALTH)"
    FAILED=1
  fi
done

if [ $FAILED -eq 1 ]; then
  echo "Some services are not healthy."
  exit 1
else
  echo "All services are up."
fi
