#!/bin/bash

# Setup script for deploying to Proxy VM
# This script should be run on the Proxy VM after cloning the repository

set -e

echo "=========================================="
echo "Setting up Proxy VM"
echo "=========================================="
echo ""

# Check if variables are provided
if [ -z "$APP_VM_HOST" ]; then
    echo "ERROR: APP_VM_HOST environment variable not set"
    echo "Usage: APP_VM_HOST=<ip-or-hostname> GRAFANA_PASSWORD=<password> bash setup-proxy-vm.sh"
    exit 1
fi

echo "App VM Host: $APP_VM_HOST"
echo ""

# Create .env.proxy
echo "Creating .env.proxy..."
cat > .env.proxy << EOF
SHA_TAG=sha-latest
APP_VM_HOST=$APP_VM_HOST
GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-admin}
EOF

echo "✓ .env.proxy created"
echo ""

# Generate nginx config from template
echo "Generating nginx.conf from template..."
export APP_VM_HOST

envsubst '${APP_VM_HOST}' < reverse-proxy/nginx.conf.template > reverse-proxy/nginx.conf

echo "✓ nginx.conf generated"
echo ""

# Check Docker and Docker Compose
echo "Checking Docker installation..."
docker --version
docker compose --version
echo "✓ Docker is installed"
echo ""

# Test connectivity to App VM
echo "Testing connectivity to App VM ($APP_VM_HOST)..."
if docker run --rm --network host curlimages/curl -m 5 http://$APP_VM_HOST:5000/docs > /dev/null 2>&1; then
    echo "✓ Can reach App VM on port 5000"
else
    echo "⚠ Warning: Could not reach App VM. Make sure it's running and IP is correct."
fi
echo ""

# Start containers
echo "Starting Proxy VM containers..."
docker compose -f docker-compose.proxy.yml pull
docker compose -f docker-compose.proxy.yml up -d

echo ""
echo "✓ Proxy VM started successfully!"
echo ""

# Show status
docker compose -f docker-compose.proxy.yml ps
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Access points:"
echo "  - Web app: http://localhost/"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "View logs:"
echo "  docker compose -f docker-compose.proxy.yml logs -f"
echo ""
