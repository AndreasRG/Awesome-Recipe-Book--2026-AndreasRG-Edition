#!/bin/bash

# Setup script for deploying to App VM
# This script should be run on the App VM after cloning the repository

set -e

echo "=========================================="
echo "Setting up App VM"
echo "=========================================="
echo ""

# Create .env.app
echo "Creating .env.app..."
cat > .env.app << EOF
SHA_TAG=sha-latest
EOF

echo "✓ .env.app created"
echo ""

# Check Docker and Docker Compose
echo "Checking Docker installation..."
docker --version
docker compose --version
echo "✓ Docker is installed"
echo ""

# Start containers
echo "Starting App VM containers..."
docker compose -f docker-compose.app.yml pull
docker compose -f docker-compose.app.yml up -d

echo ""
echo "✓ App VM started successfully!"
echo ""

# Show status
docker compose -f docker-compose.app.yml ps
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "App instances are running:"
echo "  - app1: http://localhost:5001/"
echo "  - app2: http://localhost:5002/"
echo "  - app3: http://localhost:5003/"
echo ""
echo "Monitoring is centralized on Proxy VM"
echo ""
echo "View logs:"
echo "  docker compose -f docker-compose.app.yml logs -f"
echo ""
