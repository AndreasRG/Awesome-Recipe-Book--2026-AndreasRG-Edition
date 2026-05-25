# Quick Start Guide - 2-VM Deployment

## 📋 Checklist

- [ ] Update GitHub Secrets with VM IPs, SSH credentials
- [ ] SSH into **App VM** and clone repository
- [ ] SSH into **Proxy VM** and clone repository
- [ ] Run setup script on App VM
- [ ] Run setup script on Proxy VM
- [ ] Test connectivity between VMs
- [ ] Verify web app is accessible through Proxy VM

---

## 🚀 One-Command Setup (if everything is ready)

### On App VM:
```bash
cd ~/Awesome-Recipe-Book--2026-AndreasRG-Edition
bash setup-app-vm.sh
```

### On Proxy VM:
```bash
cd ~/Awesome-Recipe-Book--2026-AndreasRG-Edition
APP_VM_HOST=<app-ip> GRAFANA_PASSWORD="your-password" bash setup-proxy-vm.sh
```

---

## 🔍 Verify Everything Works

### 1. Check containers are running:

**App VM:**
```bash
docker compose -f docker-compose.app.yml ps
```

Expected output: `app1`, `app2`, `app3`, `node-exporter-app`

**Proxy VM:**
```bash
docker compose -f docker-compose.proxy.yml ps
```

Expected output: `reverse-proxy`, `prometheus-proxy`, `grafana-proxy`, `node-exporter-proxy`

### 2. Test nginx can reach apps:

**From Proxy VM:**
```bash
curl http://<app-vm-ip>:5001/docs
```

**From outside (through proxy):**
```bash
curl http://<proxy-vm-ip>/docs
```

### 3. Access the dashboard:

- **Web App**: `http://<proxy-vm-ip>/`
- **Prometheus**: `http://<proxy-vm-ip>:9090` (centralized metrics)
- **Grafana**: `http://<proxy-vm-ip>:3000` (centralized dashboard)

---

## 🔧 Required GitHub Secrets

Set these in: Settings → Secrets and variables → Actions

| Secret | Value |
|--------|-------|
| `GHCR_TOKEN` | Personal access token from GitHub with `write:packages` scope |
| `SSH_PRIVATE_KEY` | Private SSH key (use `cat ~/.ssh/id_rsa \| sed ':a;N;$!ba;s/\n/\\n/g'` to format) |
| `PROXY_VM_HOST` | IP or hostname of Proxy VM |
| `PROXY_VM_USER` | SSH user for Proxy VM (e.g., `ubuntu`) |
| `APP_VM_HOST` | IP or hostname of App VM |
| `APP_VM_USER` | SSH user for App VM |
| `GRAFANA_PASSWORD` | (Optional) Grafana admin password |

---

## 📊 Architecture at a Glance

```
┌─ GitHub (push to main)
│
├─► Build Docker image
│
├─► Deploy to App VM
│   └─ Run: app1, app2, app3, node-exporter-app
│
└─► Deploy to Proxy VM
    └─ Run: reverse-proxy (nginx), prometheus, grafana, node-exporter-proxy
       └─ nginx proxies traffic to App VM
       └─ prometheus scrapes metrics from both VMs + all app instances
```

---

## 🐛 Common Issues

| Nginx gives 502 Bad Gateway | Check `APP_VM_HOST` in `.env.proxy`. Verify App VM is running. Test: `docker exec reverse-proxy curl http://<app-vm-ip>:5001/` |
| Containers won't start | Check `.env` files. Run `docker compose logs` to see errors. |
| GitHub Actions deployment fails | Check SSH credentials in secrets. Verify SSH keys are authorized on both VMs. |
| Can't reach App VM from Proxy VM | Check firewall rules. Ping the App VM: `ping <app-vm-ip>`. Verify Docker is running on App VM. |
| Prometheus can't scrape app metrics | Verify `APP_VM_HOST` in prometheus.proxy.yml config. Ensure app ports 5001, 5002, 5003 are exposed. |

---

## 📝 File Reference

| File | Purpose |
|------|---------|
| `docker-compose.app.yml` | Services for App VM (3 apps + node-exporter) |
| `docker-compose.proxy.yml` | Services for Proxy VM (nginx + centralized monitoring) |
| `reverse-proxy/nginx.conf.template` | Template for nginx config (with env var substitution) |
| `reverse-proxy/nginx.conf` | Generated nginx config (don't edit directly) |
| `monitoring/prometheus.proxy.yml` | Prometheus config for Proxy VM (scrapes both VMs) |
| `.github/workflows/cd.yml` | CI/CD pipeline (auto-deploys to both VMs) |
| `setup-app-vm.sh` | Setup script for App VM |
| `setup-proxy-vm.sh` | Setup script for Proxy VM |
| `DEPLOYMENT_2VM_SETUP.md` | Detailed setup guide |
| `ENV_VARIABLES.md` | Environment variable reference |

---

## 🔄 Auto-Deployment Workflow

```
You push to main
       ↓
GitHub Actions runs:
       ↓
1. Build Docker image → Push to GHCR
       ↓
2. SSH to App VM → Pull image → `docker compose up -d`
       ↓
3. SSH to Proxy VM → Generate nginx config → `docker compose up -d`
       ↓
✅ Both VMs updated automatically
```

---

## 📚 Need More Help?

- **Full setup guide**: See [DEPLOYMENT_2VM_SETUP.md](DEPLOYMENT_2VM_SETUP.md)
- **Environment variables**: See [ENV_VARIABLES.md](ENV_VARIABLES.md)
- **Docker Compose docs**: https://docs.docker.com/compose/
- **Nginx docs**: https://nginx.org/en/docs/
