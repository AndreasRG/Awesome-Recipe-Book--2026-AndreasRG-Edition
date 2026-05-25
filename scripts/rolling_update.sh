#!/bin/bash

# Always run from repo root
cd "$(dirname "$0")/.."

force_update_service() {
  SERVICE=$1
  echo "FORCE updating $SERVICE..."

  # If the service does not exist or is not running, recreate it using fallback templates
  if ! docker ps -a --format '{{.Names}}' | grep -q "^${SERVICE}$"; then
    echo "$SERVICE does not exist. Attempting to recreate using fallback templates..."

    TEMPLATE=""

    # Try app3 first
    if docker ps -a --format '{{.Names}}' | grep -q "^app3$"; then
      TEMPLATE="app3"
    # If app3 doesn't exist, try app2
    elif docker ps -a --format '{{.Names}}' | grep -q "^app2$"; then
      TEMPLATE="app2"
    fi

    # If no template exists, abort
    if [ -z "$TEMPLATE" ]; then
      echo "ERROR: No template apps exist, manual fix required!"
      exit 1
    fi

    echo "Using $TEMPLATE as template for recreating $SERVICE..."

    # Get image from template
    IMAGE=$(docker inspect --format='{{.Config.Image}}' $TEMPLATE 2>/dev/null)

    if [ -z "$IMAGE" ]; then
      echo "ERROR: Could not determine image from $TEMPLATE. Aborting."
      exit 1
    fi

    echo "Using image: $IMAGE"

    # Recreate the missing service
    docker compose -f docker-compose.app.yml up -d --no-deps --force-recreate $SERVICE
  fi

  # Now perform the normal forced update
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
