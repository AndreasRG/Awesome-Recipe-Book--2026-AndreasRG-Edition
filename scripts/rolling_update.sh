#!/bin/bash

# Always run from repo root
cd "$(dirname "$0")/.."

force_update_service() {
  SERVICE=$1
  echo "FORCE updating $SERVICE..."

  # ---------------------------------------------------------
  # CASE 1: app1 DOES NOT EXIST → skip update, go to recovery
  # ---------------------------------------------------------
  if ! docker ps -a --format '{{.Names}}' | grep -q "^${SERVICE}$"; then
    echo "$SERVICE does not exist. Skipping update and attempting recovery..."
    recover_service_from_templates "$SERVICE"
    return 1
  fi

  # ---------------------------------------------------------
  # CASE 2: app1 EXISTS → try normal update first
  # ---------------------------------------------------------
  docker compose -f docker-compose.app.yml up -d --force-recreate --no-deps $SERVICE

  echo "Waiting for $SERVICE to become healthy..."
  while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)

    if [ "$STATUS" = "healthy" ]; then
      echo "$SERVICE is healthy after normal update!"
      return 0
    fi

    if [ "$STATUS" = "unhealthy" ]; then
      echo "ERROR: $SERVICE failed health check after normal update."
      break
    fi

    sleep 2
  done

  # ---------------------------------------------------------
  # CASE 3: Normal update FAILED → recovery mode
  # ---------------------------------------------------------
  echo "Aborting rolling update. Attempting to recover $SERVICE from template..."
  recover_service_from_templates "$SERVICE"
  return 1
}

recover_service_from_templates() {
  SERVICE=$1

  TEMPLATE=""

  # Try app3 first
  if docker ps -a --format '{{.Names}}' | grep -q "^app3$"; then
    TEMPLATE="app3"
  # Then app2
  elif docker ps -a --format '{{.Names}}' | grep -q "^app2$"; then
    TEMPLATE="app2"
  fi

  # No templates available
  if [ -z "$TEMPLATE" ]; then
    echo "ERROR: No template apps exist, manual fix required!"
    docker stop $SERVICE 2>/dev/null || true
    docker rm $SERVICE 2>/dev/null || true
    exit 1
  fi

  echo "Using $TEMPLATE as template to recreate $SERVICE..."

  # Remove broken/missing container
  docker stop $SERVICE 2>/dev/null || true
  docker rm $SERVICE 2>/dev/null || true

  # Recreate from compose
  docker compose -f docker-compose.app.yml up -d --no-deps --force-recreate $SERVICE

  echo "Waiting for recovered $SERVICE to become healthy..."
  while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)

    if [ "$STATUS" = "healthy" ]; then
      echo "$SERVICE successfully recovered from $TEMPLATE. Rolling update will NOT continue."
      return 0
    fi

    if [ "$STATUS" = "unhealthy" ]; then
      echo "ERROR: $SERVICE failed health check even after recovery from $TEMPLATE. Manual fix required."
      docker stop $SERVICE 2>/dev/null || true
      docker rm $SERVICE 2>/dev/null || true
      exit 1
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
    echo "ERROR: $PREVIOUS is NOT healthy. Aborting deployment."
    exit 1
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

    if [ "$STATUS" = "unhealthy" ]; then
      echo "ERROR: $SERVICE failed health check. Aborting deployment and shutting down unhealthy $SERVICE."
      docker stop $SERVICE
      docker rm $SERVICE
      exit 1
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
