#!/bin/bash

# Quick fix script to regenerate nginx config and restart reverse-proxy

set -e

echo "Regenerating nginx.conf from template..."

# Get APP_VM_HOST from .env.proxy or ask user
if [ -f ".env.proxy" ]; then
    APP_VM_HOST=$(grep APP_VM_HOST .env.proxy | cut -d '=' -f2)
    echo "Using APP_VM_HOST from .env.proxy: $APP_VM_HOST"
else
    echo "ERROR: .env.proxy not found"
    echo "Please set APP_VM_HOST environment variable or create .env.proxy"
    exit 1
fi

# Generate the nginx config
export APP_VM_HOST
envsubst '${APP_VM_HOST}' < reverse-proxy/nginx.conf.template > reverse-proxy/nginx.conf

echo "✓ nginx.conf regenerated"
echo ""

# Restart the reverse-proxy container
echo "Restarting reverse-proxy container..."
docker compose -f docker-compose.proxy.yml restart reverse-proxy

echo ""
echo "✓ reverse-proxy restarted"
echo ""
echo "Checking reverse-proxy status..."
docker compose -f docker-compose.proxy.yml ps reverse-proxy
