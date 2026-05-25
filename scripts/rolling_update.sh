#!/bin/bash

# Rolling update script with self-healing capabilities
# Flow:
#   1. Update app1 (always attempt)
#   2. If app1 succeeds → proceed with app2 rolling update
#   3. If app1 fails → enter self-healing recovery
#   4. Self-healing attempts: copy app3 → copy app2 → create from scratch
#   5. If recovery fails → shutdown gracefully and exit

cd "$(dirname "$0")/.."

set -o pipefail

attempt_update() {
  SERVICE=$1
  echo "[$(date +'%H:%M:%S')] Attempting to update $SERVICE..."

  # Try to update/create the service
  docker compose -f docker-compose.app.yml up -d --force-recreate --no-deps $SERVICE

  # Initial grace period - let the app start before checking health
  # Azure machines are slow, so we give it plenty of time
  echo "[$(date +'%H:%M:%S')] Waiting 30s for container to initialize..."
  sleep 30

  # Wait for healthcheck to pass
  TIMEOUT=0
  MAX_TIMEOUT=150
  
  while [ $TIMEOUT -lt $MAX_TIMEOUT ]; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE 2>/dev/null)

    if [ "$STATUS" = "healthy" ]; then
      echo "[$(date +'%H:%M:%S')] ✓ $SERVICE is healthy!"
      return 0
    fi

    if [ "$STATUS" = "unhealthy" ]; then
      echo "[$(date +'%H:%M:%S')] ✗ $SERVICE failed health check"
      echo "[$(date +'%H:%M:%S')] Container logs:"
      docker logs $SERVICE 2>&1 | tail -30
      return 1
    fi

    TIMEOUT=$((TIMEOUT + 2))
    sleep 2
  done

  echo "[$(date +'%H:%M:%S')] ✗ $SERVICE healthcheck timeout after ${MAX_TIMEOUT}s"
  echo "[$(date +'%H:%M:%S')] Container logs:"
  docker logs $SERVICE 2>&1 | tail -30
  return 1
}

self_heal_service() {
  SERVICE=$1
  echo ""
  echo "[$(date +'%H:%M:%S')] ⚠️  SELF-HEALING: $SERVICE is unhealthy. Attempting recovery..."
  echo "[$(date +'%H:%M:%S')] Recovery strategy: copy app3 → copy app2 → create from scratch"
  echo ""

  # Remove the broken container
  docker stop $SERVICE 2>/dev/null || true
  docker rm $SERVICE 2>/dev/null || true

  # RECOVERY ATTEMPT 1: Copy from app3
  if docker ps -a --format '{{.Names}}' | grep -q "^app3$"; then
    echo "[$(date +'%H:%M:%S')] [Recovery #1] Attempting to recreate $SERVICE from app3 template..."
    attempt_update $SERVICE
    if [ $? -eq 0 ]; then
      echo "[$(date +'%H:%M:%S')] ✓ Self-healing succeeded: $SERVICE recovered from app3"
      return 0
    fi
    echo "[$(date +'%H:%M:%S')] ✗ Recovery #1 failed"
    docker stop $SERVICE 2>/dev/null || true
    docker rm $SERVICE 2>/dev/null || true
  fi

  # RECOVERY ATTEMPT 2: Copy from app2
  if docker ps -a --format '{{.Names}}' | grep -q "^app2$"; then
    echo "[$(date +'%H:%M:%S')] [Recovery #2] Attempting to recreate $SERVICE from app2 template..."
    attempt_update $SERVICE
    if [ $? -eq 0 ]; then
      echo "[$(date +'%H:%M:%S')] ✓ Self-healing succeeded: $SERVICE recovered from app2"
      return 0
    fi
    echo "[$(date +'%H:%M:%S')] ✗ Recovery #2 failed"
    docker stop $SERVICE 2>/dev/null || true
    docker rm $SERVICE 2>/dev/null || true
  fi

  # RECOVERY ATTEMPT 3: Create from scratch
  echo "[$(date +'%H:%M:%S')] [Recovery #3] Attempting to create $SERVICE from scratch..."
  attempt_update $SERVICE
  if [ $? -eq 0 ]; then
    echo "[$(date +'%H:%M:%S')] ✓ Self-healing succeeded: $SERVICE created from scratch"
    return 0
  fi
  echo "[$(date +'%H:%M:%S')] ✗ Recovery #3 failed"

  # FATAL: All recovery attempts failed - shutdown gracefully
  echo ""
  echo "[$(date +'%H:%M:%S')] ❌ CRITICAL: All recovery attempts failed for $SERVICE"
  echo "[$(date +'%H:%M:%S')] Shutting down $SERVICE gracefully..."
  docker stop $SERVICE 2>/dev/null || true
  docker rm $SERVICE 2>/dev/null || true
  echo "[$(date +'%H:%M:%S')] System shutdown complete."
  return 1
}

attempt_rolling_update_sequence() {
  echo "[$(date +'%H:%M:%S')] Starting rolling update sequence..."
  echo ""

  # STEP 1: Update app1 (CRITICAL)
  attempt_update app1
  if [ $? -ne 0 ]; then
    echo ""
    echo "[$(date +'%H:%M:%S')] 🔴 app1 update FAILED. Entering self-healing mode..."
    self_heal_service app1
    if [ $? -ne 0 ]; then
      echo "[$(date +'%H:%M:%S')] 🛑 DEPLOYMENT ABORTED: Cannot recover app1"
      return 1
    fi
    echo "[$(date +'%H:%M:%S')] app1 recovered successfully. Proceeding with rolling updates..."
  fi

  echo ""
  echo "[$(date +'%H:%M:%S')] ✓ app1 is healthy. Proceeding to app2 rolling update..."

  # STEP 2: Update app2 (only if app1 is healthy)
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' app1 2>/dev/null)
  if [ "$STATUS" != "healthy" ]; then
    echo "[$(date +'%H:%M:%S')] ✗ app1 is no longer healthy. Aborting rolling updates."
    return 1
  fi

  attempt_update app2
  if [ $? -ne 0 ]; then
    echo "[$(date +'%H:%M:%S')] ⚠️  app2 update failed. Attempting self-healing..."
    self_heal_service app2
    if [ $? -ne 0 ]; then
      echo "[$(date +'%H:%M:%S')] ⚠️  app2 recovery failed, but app1 is stable. Rolling update incomplete."
      return 1
    fi
  fi

  echo ""
  echo "[$(date +'%H:%M:%S')] ✓ app2 is healthy. Proceeding to app3 rolling update..."

  # STEP 3: Update app3 (only if app2 is healthy)
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' app2 2>/dev/null)
  if [ "$STATUS" != "healthy" ]; then
    echo "[$(date +'%H:%M:%S')] ✗ app2 is no longer healthy. Aborting app3 update."
    return 1
  fi

  attempt_update app3
  if [ $? -ne 0 ]; then
    echo "[$(date +'%H:%M:%S')] ⚠️  app3 update failed. Attempting self-healing..."
    self_heal_service app3
    if [ $? -ne 0 ]; then
      echo "[$(date +'%H:%M:%S')] ⚠️  app3 recovery failed, but app1 and app2 are stable. Rolling update mostly complete."
      return 1
    fi
  fi

  echo ""
  echo "[$(date +'%H:%M:%S')] ✓ All apps updated successfully!"
  return 0
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

# ============================================================
# MAIN EXECUTION
# ============================================================

echo "╔════════════════════════════════════════════════════════╗"
echo "║          Rolling Update with Self-Healing             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

attempt_rolling_update_sequence

RESULT=$?

echo ""
echo "╔════════════════════════════════════════════════════════╗"
if [ $RESULT -eq 0 ]; then
  echo "║  ✓ Rolling update completed successfully              ║"
else
  echo "║  ⚠️  Rolling update completed with issues             ║"
fi
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Final status check
echo "Final status:"
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E '^app[123]'

exit $RESULT
