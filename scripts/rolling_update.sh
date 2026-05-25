#!/bin/bash

# Always run from repo root
cd "$(dirname "$0")/.."


update_service() {
  SERVICE=$1
  echo "Updating $SERVICE..."

  docker compose up -d $SERVICE

  echo "Waiting for $SERVICE to become healthy..."
  while true; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' $SERVICE)
    if [ "$STATUS" = "healthy" ]; then
      echo "$SERVICE is healthy!"
      break
    fi
    sleep 2
  done
}

update_service app1
update_service app2
update_service app3

echo "Rolling update complete."
