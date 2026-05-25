# 2-VM Architecture Setup Guide

## Overview

The application has been restructured from a single-VM monolithic deployment to a **2-VM microservices architecture**:

- **VM1 - Proxy VM**: Runs nginx reverse proxy + centralized monitoring stack (Prometheus, Grafana, node-exporter)
- **VM2 - App VM**: Runs 3 application instances only + node-exporter for metrics collection

The Proxy VM monitors both VMs and all application instances. Both VMs automatically update on push to `main` branch via GitHub Actions.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      GitHub Actions                      │
│                   (on push to main)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    ┌───▼──────────────┐       ┌──────▼─────────────┐
    │   PROXY VM (VM1) │       │    APP VM (VM2)    │
    ├──────────────────┤       ├────────────────────┤
    │ nginx (port 80)  │◄─────►│ app1 (port 5001)   │
    │ Prometheus 9090  │       │ app2 (port 5002)   │
    │ Grafana 3000     │       │ app3 (port 5003)   │
    │ node-exporter    │       │ node-exporter 9100 │
    │                  │       │                    │
    │ (Monitors both)  │       │ (Metrics only)     │
    └────────────────┬─┘       └────────────────────┘
                     │
              (public endpoint)
```

**Key Points:**
- Prometheus on Proxy VM scrapes metrics from:
  - nginx reverse proxy
  - App VM node-exporter (9100)
  - Proxy VM node-exporter (9100)
  - All 3 app instances (5001, 5002, 5003)
- Single Grafana dashboard centrally managed
- Reduced resource usage (no duplicate monitoring)

---

## Prerequisites

### For Each VM:
- Docker & Docker Compose installed
- Git repository cloned: `git clone https://github.com/AndreasRG/Awesome-Recipe-Book--2026-AndreasRG-Edition.git`
- `.env.proxy` or `.env.app` file configured (see below)
- SSH access for automated deployments

### GitHub Secrets (for automated deployment):
```
GHCR_TOKEN               # GitHub Container Registry token
PROXY_VM_HOST            # IP/hostname of Proxy VM
PROXY_VM_USER            # SSH user for Proxy VM
APP_VM_HOST              # IP/hostname of App VM
APP_VM_USER              # SSH user for App VM
SSH_PRIVATE_KEY          # SSH private key for authentication
GRAFANA_PASSWORD         # Grafana admin password (optional, defaults to 'admin')
```

---

## Setup Instructions

### Step 1: Network Configuration

Before deploying, you need to know:
- **Proxy VM IP/hostname**: `<PROXY_VM_HOST>`
- **App VM IP/hostname**: `<APP_VM_HOST>`

These should be the **internal network IPs** if both VMs are on the same network, or **public IPs** if they're remote.

### Step 2: Deploy to APP VM

On the **APP VM**, create `.env.app`:
```bash
cd ~/Awesome-Recipe-Book--2026-AndreasRG-Edition
cat > .env.app << EOF
SHA_TAG=sha-latest
EOF
```

Then start the containers:
```bash
docker compose -f docker-compose.app.yml pull
docker compose -f docker-compose.app.yml up -d
```

Verify:
```bash
docker compose -f docker-compose.app.yml ps
```

Expected containers: `app1`, `app2`, `app3`, `node-exporter-app`

### Step 3: Deploy to PROXY VM

On the **PROXY VM**, create `.env.proxy`:
```bash
cd ~/Awesome-Recipe-Book--2026-AndreasRG-Edition
cat > .env.proxy << EOF
SHA_TAG=sha-latest
APP_VM_HOST=<IP_OF_APP_VM>
GRAFANA_PASSWORD=your-secure-password
EOF
```

Generate the nginx config from the template:
```bash
APP_VM_HOST=<IP_OF_APP_VM> envsubst '${APP_VM_HOST}' < reverse-proxy/nginx.conf.template > reverse-proxy/nginx.conf
```

Then start the containers:
```bash
docker compose -f docker-compose.proxy.yml pull
docker compose -f docker-compose.proxy.yml up -d
```

Verify:
```bash
docker compose -f docker-compose.proxy.yml ps
```

Expected containers: `reverse-proxy`, `prometheus-proxy`, `grafana-proxy`, `node-exporter-proxy`

### Step 4: Test Connectivity

1. **From Proxy VM**, test that nginx can reach the app VM:
   ```bash
   curl http://<APP_VM_HOST>:5001/docs
   ```

2. **From outside**, test through the proxy:
   ```bash
   curl http://<PROXY_VM_HOST>/docs
   ```

3. Access the web application:
   ```
   http://<PROXY_VM_HOST>/
   ```

---

## Monitoring

All monitoring is centralized on the **Proxy VM** for simplicity and reduced resource overhead.

### Prometheus on Proxy VM
- **URL**: `http://<PROXY_VM_HOST>:9090`
- **Metrics scraped from**:
  - nginx reverse proxy metrics
  - Proxy VM node exporter (9100)
  - App VM node exporter (9100, remote)
  - All 3 application instances (ports 5001, 5002, 5003)

### Grafana on Proxy VM
- **URL**: `http://<PROXY_VM_HOST>:3000`
- **Default credentials**: `admin` / `admin` (or `GRAFANA_PASSWORD`)
- **Single dashboard** with metrics from both VMs and all app instances

**Note:** The App VM runs only node-exporter for metrics collection. All visualization and alerting is done centrally on the Proxy VM.

---

## Automatic Deployments

When you push to the `main` branch:

1. **Build Job**: Docker image is built and pushed to GHCR
2. **Deploy App VM Job**: 
   - SSH into App VM
   - Creates `.env.app` with `SHA_TAG`
   - Pulls new image and restarts containers
3. **Deploy Proxy VM Job**:
   - SSH into Proxy VM
   - Creates `.env.proxy` with `APP_VM_HOST` and Grafana password
   - Generates nginx config with environment variables
   - Pulls new image and restarts containers

Both deployment jobs run in parallel after the build completes.

---

## File Structure

```
.
├── docker-compose.app.yml          # App VM services (3 app instances + node-exporter)
├── docker-compose.proxy.yml        # Proxy VM services (nginx + centralized monitoring)
├── .github/workflows/cd.yml        # CI/CD pipeline (updated for 2 VMs)
├── reverse-proxy/
│   ├── nginx.conf                  # Generated from template (git-ignored)
│   └── nginx.conf.template         # Template with env var substitution
├── monitoring/
│   ├── prometheus.proxy.yml        # Prometheus config for Proxy VM (scrapes both VMs)
│   └── prometheus.yml.save         # Legacy (can be removed)
└── ... (other files)
```

---

## Troubleshooting

### Nginx can't reach app instances
- Verify `APP_VM_HOST` is correct and accessible from Proxy VM
- Test: `docker exec reverse-proxy curl http://<APP_VM_HOST>:5001/docs`
- Check firewall rules between VMs
- Ensure `docker-compose.app.yml` has containers running with exposed ports

### Containers won't start
- Check `.env` files have correct variables
- Verify GHCR image pull access: `docker login ghcr.io`
- Check Docker Compose version: `docker compose --version` (should be v2+)
- Review logs: `docker compose -f docker-compose.app.yml logs`

### Monitoring not working
- Verify Prometheus config files have correct target hosts
- Use private IP addresses for internal communication between VMs
- Check that node-exporter is running on both VMs
- Grafana may take a minute to start, then add data source

### Deployment fails
- Check SSH credentials in GitHub Secrets
- Verify SSH key has correct permissions: `chmod 600 ~/.ssh/id_rsa`
- Review GitHub Actions logs for error messages
- Ensure both VMs have git repository already cloned

---

## Rollback

If something goes wrong, rollback by deploying a previous image tag:

```bash
# On App VM
SHA_TAG=sha-<previous-commit-hash> docker compose -f docker-compose.app.yml up -d

# On Proxy VM
SHA_TAG=sha-<previous-commit-hash> docker compose -f docker-compose.proxy.yml up -d
```

---

## Migration from Single VM (Legacy)

If migrating from the old `docker-compose.yml`:

1. **On new App VM**:
   - Pull the repository
   - Copy database if needed
   - Run `docker compose -f docker-compose.app.yml up -d`

2. **On new Proxy VM**:
   - Pull the repository
   - Configure `APP_VM_HOST` environment variable
   - Run `docker compose -f docker-compose.proxy.yml up -d`

3. **Update DNS/Load Balancer** to point to new Proxy VM IP

4. **Keep old VM as backup** until everything is verified working

---

## Next Steps

- [ ] Configure SSL/HTTPS in nginx (see `reverse-proxy/nginx.conf.template` for commented examples)
- [ ] Set up persistent storage for Grafana dashboards
- [ ] Configure alerting in Prometheus
- [ ] Implement custom health check endpoints in FastAPI
- [ ] Add log aggregation (ELK stack, Loki, etc.)
- [ ] Consider Redis cache between VMs if needed
