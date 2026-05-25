#!/bin/bash

# Always run from repo root
cd "$(dirname "$0")/.."

set -o pipefail

force_update_service() {
  SERVICE=$1
  echo "FORCE updating $SERVICE..."

  # ---------------------------------------------------------
  # CASE 1: app1 DOES NOT EXIST → skip update, go to recovery
  # ---------------------------------------------------------
  if ! docker ps -a --format '{{.Names}}' | grep -q "^${SERVICE}$"; then
    echo "$SERVICE does not exist. Attempting recovery..."
    recover_service_from_templates "$SERVICE"
    return $?
  fi

  # ---------------------------------------------------------
  # CASE 2: app1 EXISTS → try normal update first
  # ---------------------------------------------------------
  docker compose -f docker-compose.app.yml up -d --force-recreate --no-deps $SERVICE

  echo "Waiting for $SERVICE to become healthy..."
  TIMEOUT=0
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

    TIMEOUT=$((TIMEOUT + 1))
    if [ $TIMEOUT -gt 30 ]; then
      echo "WARNING: $SERVICE healthcheck timeout. Attempting recovery..."
      break
    fi

    sleep 2
  done

  # ---------------------------------------------------------
  # CASE 3: Normal update FAILED → recovery mode
  # ---------------------------------------------------------
  echo "Aborting normal update. Attempting to recover $SERVICE from template..."
  recover_service_from_templates "$SERVICE"
  return $?
}

recover_service_from_templates() {
  SERVICE=$1
  TEMPLATE=""

  # Try app3 first, then app2
  if docker ps -a --format '{{.Names}}' | grep -q "^app3$"; then
    TEMPLATE="app3"
  elif docker ps -a --format '{{.Names}}' | grep -q "^app2$"; then
    TEMPLATE="app2"
  fi

  # No templates available - do a clean creation from scratch
  if [ -z "$TEMPLATE" ]; then
    echo "WARNING: No template apps exist. Creating $SERVICE from scratch..."
    
    # Remove any broken/partial containers
    docker stop $SERVICE 2>/dev/null || true
    docker rm $SERVICE 2>/dev/null || true
    
    # Create from docker-compose
    docker compose -f docker-compose.app.yml up -d --no-deps $SERVICE
    
    echo "Waiting for $SERVICE to become healthy (created from scratch)..."
    TIMEOUT=0
    while true; do
      STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)

      if [ "$STATUS" = "healthy" ]; then
        echo "$SERVICE successfully created and is healthy!"
        return 0
      fi

      if [ "$STATUS" = "unhealthy" ]; then
        echo "ERROR: $SERVICE failed health check even when created from scratch."
        echo "Container logs:"
        docker logs $SERVICE | tail -20
        return 1
      fi

      TIMEOUT=$((TIMEOUT + 1))
      if [ $TIMEOUT -gt 30 ]; then
        echo "ERROR: $SERVICE healthcheck timeout. Cannot recover."
        docker logs $SERVICE | tail -20
        return 1
      fi

      sleep 2
    done
  fi

  echo "Using $TEMPLATE as template to recreate $SERVICE..."

  # Remove broken/missing container
  docker stop $SERVICE 2>/dev/null || true
  docker rm $SERVICE 2>/dev/null || true

  # Recreate from compose
  docker compose -f docker-compose.app.yml up -d --no-deps --force-recreate $SERVICE

  echo "Waiting for recovered $SERVICE to become healthy..."
  TIMEOUT=0
  while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)

    if [ "$STATUS" = "healthy" ]; then
      echo "$SERVICE successfully recovered from $TEMPLATE!"
      return 0
    fi

    if [ "$STATUS" = "unhealthy" ]; then
      echo "ERROR: $SERVICE failed health check after recovery attempt."
      docker logs $SERVICE | tail -20
      return 1
    fi

    TIMEOUT=$((TIMEOUT + 1))
    if [ $TIMEOUT -gt 30 ]; then
      echo "ERROR: $SERVICE healthcheck timeout during recovery."
      docker logs $SERVICE | tail -20
      return 1
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
    echo "ERROR: $PREVIOUS is NOT healthy. Aborting $SERVICE update."
    return 1
  fi

  echo "$PREVIOUS is healthy. Updating $SERVICE..."

  docker compose -f docker-compose.app.yml up -d --force-recreate --no-deps $SERVICE

  echo "Waiting for $SERVICE to become healthy..."
  TIMEOUT=0
  while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)
    if [ "$STATUS" = "healthy" ]; then
      echo "$SERVICE is healthy!"
      return 0
    fi

    if [ "$STATUS" = "unhealthy" ]; then
      echo "ERROR: $SERVICE failed health check. Aborting."
      docker logs $SERVICE | tail -20
      return 1
    fi

    TIMEOUT=$((TIMEOUT + 1))
    if [ $TIMEOUT -gt 30 ]; then
      echo "ERROR: $SERVICE healthcheck timeout."
      return 1
    fi

    sleep 2
  done
}


# 1. app1 ALWAYS updates (even from scratch if needed)
force_update_service app1
APP1_RESULT=$?

# 2. app2 ONLY updates if app1 is healthy
if [ $APP1_RESULT -eq 0 ]; then
  update_service_if_healthy app2 app1
  APP2_RESULT=$?
else
  echo "Skipping app2 update because app1 is not healthy"
  APP2_RESULT=1
fi

# 3. app3 ONLY updates if app2 is healthy
if [ $APP2_RESULT -eq 0 ]; then
  update_service_if_healthy app3 app2
  APP3_RESULT=$?
else
  echo "Skipping app3 update because app2 is not healthy"
  APP3_RESULT=1
fi

# Summary
echo ""
echo "========================================"
echo "Rolling update summary:"
echo "  app1: $([ $APP1_RESULT -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')"
echo "  app2: $([ $APP2_RESULT -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')"
echo "  app3: $([ $APP3_RESULT -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')"
echo "========================================"

if [ $APP1_RESULT -ne 0 ]; then
  echo "CRITICAL: app1 failed to update/recover. Manual intervention required."
  exit 1
fi

exit 0
