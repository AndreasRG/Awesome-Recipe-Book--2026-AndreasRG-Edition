#!/bin/bash

# Always run from repo root
cd "$(dirname "$0")/.."

force_update_service() {
  SERVICE=$1
  echo "FORCE updating $SERVICE..."

  docker compose -f docker-compose.app.yml up -d --force-recreate --no-deps $SERVICE

  echo "Waiting for $SERVICE to become healthy..."
  while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)
    if [ "$STATUS" = "healthy" ]; then
      echo "$SERVICE is healthy!"
      break
    fi
    sleep 2
  done
}

update_service_if_healthy() {
  SERVICE=$1
  PREVIOUS=$2

  echo "Checking if $PREVIOUS is healthy before updating $SERVICE..."

  STATUS=$(docker inspect --format='{{.State.Health.Status}}' $PREVIOUS 2>/dev/null)

  if [ "$STATUS" != "healthy" ]; then
    echo "ERROR: $PREVIOUS is NOT healthy. Skipping update of $SERVICE."
    return
  fi

  echo "$PREVIOUS is healthy. Updating $SERVICE..."

  docker compose -f docker-compose.app.yml up -d --force-recreate --no-deps $SERVICE

  echo "Waiting for $SERVICE to become healthy..."
  while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)
    if [ "$STATUS" = "healthy" ]; then
      echo "$SERVICE is healthy!"
      break
    fi
    sleep 2
  done
}

# 1. app1 ALWAYS updates
force_update_service app1

# 2. app2 ONLY updates if app1 is healthy
update_service_if_healthy app2 app1

# 3. app3 ONLY updates if app2 is healthy
update_service_if_healthy app3 app2

echo "Rolling update complete."
