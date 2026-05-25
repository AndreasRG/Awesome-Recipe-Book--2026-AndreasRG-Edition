# Environment Variables Reference

## APP VM (.env.app)

```env
# Docker image tag - automatically set by CI/CD
SHA_TAG=sha-latest
```

## PROXY VM (.env.proxy)

```env
# Docker image tag - automatically set by CI/CD
SHA_TAG=sha-latest

# IP/hostname of the App VM (must be reachable from Proxy VM)
# Use internal network IP if on same network, public IP if remote
APP_VM_HOST=192.168.1.10

# Grafana admin password (optional, defaults to 'admin')
GRAFANA_PASSWORD=your-secure-password
```

## GitHub Actions Secrets

Required secrets in GitHub repository settings:

```
GHCR_TOKEN              GitHub Container Registry personal access token
PROXY_VM_HOST           IP or hostname of Proxy VM (for SSH deployment)
PROXY_VM_USER           SSH username for Proxy VM (usually 'ubuntu' or 'azureuser')
APP_VM_HOST             IP or hostname of App VM (for SSH deployment + nginx config)
APP_VM_USER             SSH username for App VM
SSH_PRIVATE_KEY         Private SSH key (with newlines as \n)
GRAFANA_PASSWORD        Admin password for Grafana (optional)
```

## How to Create SSH Private Key Secret

From GitHub Actions perspective:
1. Generate SSH key: `ssh-keygen -t rsa -b 4096 -f ~/.ssh/vm_key`
2. Copy public key to both VMs: `ssh-copy-id -i ~/.ssh/vm_key.pub user@vm-ip`
3. Read private key: `cat ~/.ssh/vm_key | tr '\n' '\\n'` (convert newlines for GitHub)
4. Add to GitHub Secrets as `SSH_PRIVATE_KEY`

Or use the following Python to convert:
```python
with open('.ssh/vm_key', 'r') as f:
    key = f.read()
    key_escaped = repr(key)[1:-1]  # Removes outer quotes
    print(key_escaped)
```
