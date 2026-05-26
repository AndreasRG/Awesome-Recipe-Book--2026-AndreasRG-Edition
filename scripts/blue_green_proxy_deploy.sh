#!/bin/bash
# Blue-Green Deployment Script for Reverse Proxy
# Ensures zero-downtime proxy updates by switching between two docker-compose configurations

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="${PROJECT_ROOT}/.active-proxy"
BLUE_COMPOSE="${PROJECT_ROOT}/docker-compose.proxy-blue.yml"
GREEN_COMPOSE="${PROJECT_ROOT}/docker-compose.proxy-green.yml"
GREEN_COMPOSE_TEMP="${PROJECT_ROOT}/docker-compose.proxy-green-with-ports.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect docker compose plugin or docker-compose binary
detect_compose() {
    if docker compose version >/dev/null 2>&1; then
        DC="docker compose"
    elif docker-compose version >/dev/null 2>&1; then
        DC="docker-compose"
    else
        log_error "Neither 'docker compose' nor 'docker-compose' is installed or in PATH"
        exit 1
    fi
}

# Determine which color is currently active
get_active_color() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        # Default to blue if no state file exists
        echo "blue"
    fi
}

# Determine the inactive color
get_inactive_color() {
    if [ "$(get_active_color)" = "blue" ]; then
        echo "green"
    else
        echo "blue"
    fi
}

# Wait for a service to be healthy
wait_for_health() {
    local container_name=$1
    local max_attempts=30
    local attempt=0

    log_info "Waiting for $container_name to be healthy..."

    while [ $attempt -lt $max_attempts ]; do
        if docker exec "$container_name" curl -f http://localhost/health >/dev/null 2>&1; then
            log_info "$container_name is healthy!"
            return 0
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done

    echo ""
    log_error "$container_name failed health checks after $max_attempts attempts"
    return 1
}

# Test if service is responding on external ports
test_external_ports() {
    log_info "Testing external port bindings (80/443)..."

    local max_attempts=10
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost/health >/dev/null 2>&1; then
            log_info "External ports (80/443) are responding correctly!"
            return 0
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done

    echo ""
    log_warn "External ports not responding yet (may still be binding)"
    return 0  # Don't fail - ports may need a moment to bind
}

# Main deployment logic
deploy_blue_green() {
    local active
    local inactive
    active=$(get_active_color)
    inactive=$(get_inactive_color)

    log_info "Current active color: $active"
    log_info "Starting deployment to $inactive..."


    # ---------------------------------------------------------
    # PRE-FLIGHT CHECK: ensure port 80 is free
    # ---------------------------------------------------------
    if sudo lsof -i :80 >/dev/null; then
    log_warn "Port 80 is in use by a ghost process. Cleaning up..."
    sudo kill -9 $(sudo lsof -t -i :80)
    fi


    # Step 1: Start the inactive color without port bindings
    log_info "Step 1: Starting $inactive service (staging)..."

    local new_container
    if [ "$inactive" = "green" ]; then
        $DC -f "$GREEN_COMPOSE" up -d
        new_container="reverse-proxy-green"
    else
        $DC -f "$BLUE_COMPOSE" up -d
        new_container="reverse-proxy-blue"
    fi

    # Step 2: Wait for the new service to be healthy
    log_info "Step 2: Waiting for $new_container health checks..."
    if ! wait_for_health "$new_container"; then
        log_error "New $inactive service failed health checks. Aborting deployment."

        # Cleanup: stop the failed service
        if [ "$inactive" = "green" ]; then
            $DC -f "$GREEN_COMPOSE" down
        else
            $DC -f "$BLUE_COMPOSE" down
        fi

        return 1
    fi

    # Step 3: Switch port bindings (brief downtime window - HTTP port 80 only)
    log_info "Step 3: Switching port bindings (port 80)..."
    log_info "  Stopping $active service (port 80 binding)..."

    if [ "$active" = "blue" ]; then
        $DC -f "$BLUE_COMPOSE" down
    else
        $DC -f "$GREEN_COMPOSE" down
    fi

    log_info "  Starting $inactive service with external port bindings..."

    if [ "$inactive" = "green" ]; then
        # Create temporary compose file with port bindings
        cp "$GREEN_COMPOSE" "$GREEN_COMPOSE_TEMP"
        sed -i 's/# No port bindings initially - ports will be added when this becomes active/ports:\n      - "80:80"\n      - "443:443"/' "$GREEN_COMPOSE_TEMP"

        # If sed didn't work (macOS BSD sed), recreate manually
        if ! grep -q "80:80" "$GREEN_COMPOSE_TEMP"; then
            cat > "$GREEN_COMPOSE_TEMP" << 'COMPOSE_EOF'
version: '3.8'

services:

  reverse-proxy-green:
    image: nginx:latest
    container_name: reverse-proxy-green
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./reverse-proxy/nginx.conf:/etc/nginx/nginx.conf:ro
    environment:
      - APP_VM_HOST=${APP_VM_HOST}
      - APP_VM_PORT=${APP_VM_PORT:-5000}
    restart: unless-stopped
    networks:
      - proxy-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 5s
      timeout: 3s
      retries: 3
      start_period: 10s

  prometheus-proxy:
    image: prom/prometheus:latest
    container_name: prometheus-proxy
    volumes:
      - ./monitoring/prometheus.proxy.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    restart: unless-stopped
    networks:
      - proxy-network

  grafana-proxy:
    image: grafana/grafana:latest
    container_name: grafana-proxy
    ports:
      - "3000:3000"
    volumes:
      - grafana-proxy-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    restart: unless-stopped
    networks:
      - proxy-network

  node-exporter-proxy:
    image: prom/node-exporter:latest
    container_name: node-exporter-proxy
    ports:
      - "9100:9100"
    restart: unless-stopped
    networks:
      - proxy-network

  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    container_name: nginx-exporter
    command:
      - "-nginx.scrape-uri=http://reverse-proxy-green/stub_status"
    ports:
      - "9113:9113"
    restart: unless-stopped
    networks:
      - proxy-network

networks:
  proxy-network:
    driver: bridge

volumes:
  grafana-proxy-data:
COMPOSE_EOF
        fi

        $DC -f "$GREEN_COMPOSE_TEMP" up -d
        rm -f "$GREEN_COMPOSE_TEMP"
    else
        $DC -f "$BLUE_COMPOSE" up -d
    fi

    # Step 4: Verify external connectivity
    log_info "Step 4: Verifying external port connectivity..."
    if ! test_external_ports; then
        log_warn "External ports slow to respond, but continuing..."
    fi

    # Step 5: Update state file
    log_info "Step 5: Updating active proxy state..."
    echo "$inactive" > "$STATE_FILE"

    log_info "Blue-Green deployment completed successfully!"
    log_info "Active color is now: $inactive"

    return 0
}

# Main execution
main() {
    log_info "========================================="
    log_info "Blue-Green Proxy Deployment"
    log_info "========================================="

    cd "$PROJECT_ROOT"

    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed or not in PATH"
        return 1
    fi

    detect_compose

    if deploy_blue_green; then
        log_info "========================================="
        log_info "Deployment successful!"
        log_info "========================================="
        return 0
    else
        log_error "========================================="
        log_error "Deployment failed!"
        log_error "========================================="
        return 1
    fi
}

main "$@"
