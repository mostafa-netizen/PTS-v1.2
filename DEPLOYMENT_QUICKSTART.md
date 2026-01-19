# Deployment Quick Start Guide

Fast-track deployment guide for experienced users.

---

## 🚀 5-Minute Deployment

### Prerequisites
- DigitalOcean account
- Domain name (optional)
- SSH access

### Step 1: Create Droplet (2 min)

```bash
# DigitalOcean Dashboard
# Create → Droplets
# Ubuntu 22.04, Basic, $12/mo (2GB RAM)
# Note IP address: YOUR_DROPLET_IP
```

### Step 2: Initial Setup (2 min)

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Run setup script
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/scripts/setup_vps.sh | bash

# Switch to app user
su - appuser
```

### Step 3: Deploy Application (1 min)

```bash
# Upload files (from local machine)
scp -r /path/to/project-latest-update/* appuser@YOUR_DROPLET_IP:/var/www/app/

# SSH back in
ssh appuser@YOUR_DROPLET_IP

# Configure environment
cd /var/www/app
cp .env.production .env
nano .env  # Edit SECRET_KEY and other settings

# Deploy
./deploy.sh
```

### Step 4: Access Application

```
http://YOUR_DROPLET_IP
```

---

## 📋 Manual Deployment Steps

### On DigitalOcean VPS:

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3.10 python3-pip python3-venv git nginx redis-server poppler-utils libgl1-mesa-glx libglib2.0-0

# 3. Create app directory
sudo mkdir -p /var/www/app
sudo chown -R $USER:$USER /var/www/app

# 4. Upload application files
# (Use SCP, Git, or SFTP)

# 5. Setup Python environment
cd /var/www/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure environment
cp .env.production .env
nano .env  # Edit configuration

# 7. Create systemd service
sudo nano /etc/systemd/system/tendon-analysis.service
# (Copy from DEPLOYMENT_GUIDE.md)

# 8. Configure Nginx
sudo nano /etc/nginx/sites-available/tendon-analysis
# (Copy from DEPLOYMENT_GUIDE.md)
sudo ln -s /etc/nginx/sites-available/tendon-analysis /etc/nginx/sites-enabled/

# 9. Start services
sudo systemctl daemon-reload
sudo systemctl enable tendon-analysis
sudo systemctl start tendon-analysis
sudo systemctl restart nginx

# 10. Check status
sudo systemctl status tendon-analysis
```

---

## 🎮 RunPod Setup (Optional)

### Quick Setup:

```bash
# 1. Create RunPod account
# https://www.runpod.io/

# 2. Deploy GPU Pod
# - Choose RTX 3070 or better
# - PyTorch template
# - 20GB disk

# 3. Get API credentials
# Settings → API Keys → Create

# 4. Configure on VPS
nano /var/www/app/.env
# Add:
# RUNPOD_API_KEY=your-key
# RUNPOD_ENDPOINT_ID=your-endpoint
# FORCE_RUNPOD=true

# 5. Restart application
sudo systemctl restart tendon-analysis
```

---

## 🔧 Essential Commands

### Service Management
```bash
# Start/Stop/Restart
sudo systemctl start tendon-analysis
sudo systemctl stop tendon-analysis
sudo systemctl restart tendon-analysis

# View status
sudo systemctl status tendon-analysis

# View logs
sudo journalctl -u tendon-analysis -f
```

### Monitoring
```bash
# Quick status
./scripts/monitor.sh status

# View logs
./scripts/monitor.sh logs

# Check resources
./scripts/monitor.sh resources

# Cleanup old files
./scripts/monitor.sh cleanup
```

### Nginx
```bash
# Test config
sudo nginx -t

# Restart
sudo systemctl restart nginx

# View logs
tail -f /var/log/nginx/tendon_error.log
```

### Redis
```bash
# Check status
redis-cli ping

# View info
redis-cli info

# Restart
sudo systemctl restart redis
```

---

## 🔒 SSL Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

---

## 🐛 Troubleshooting

### Application won't start
```bash
sudo journalctl -u tendon-analysis -n 50
sudo systemctl restart tendon-analysis
```

### 502 Bad Gateway
```bash
sudo systemctl status tendon-analysis
sudo netstat -tlnp | grep 5001
sudo systemctl restart tendon-analysis nginx
```

### Out of disk space
```bash
df -h
./scripts/monitor.sh cleanup
```

### High memory usage
```bash
htop
# Reduce workers in gunicorn_config.py
```

---

## 📊 File Locations

| Item | Location |
|------|----------|
| Application | `/var/www/app` |
| Uploads | `/var/www/app/uploads` |
| Outputs | `/var/www/app/outputs` |
| Logs | `/var/www/app/logs` |
| Config | `/var/www/app/.env` |
| Systemd Service | `/etc/systemd/system/tendon-analysis.service` |
| Nginx Config | `/etc/nginx/sites-available/tendon-analysis` |
| Nginx Logs | `/var/log/nginx/` |

---

## 💡 Tips

1. **Always use HTTPS in production** (free with Let's Encrypt)
2. **Monitor disk usage** regularly
3. **Setup automated backups** for important data
4. **Use RunPod serverless** to save costs
5. **Enable firewall** (UFW)
6. **Keep system updated** (`apt update && apt upgrade`)
7. **Monitor logs** for errors
8. **Test before deploying** updates

---

## 📚 Full Documentation

For detailed instructions, see:
- **DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **runpod/README.md** - RunPod integration guide
- **README.md** - Application documentation

---

**Need help?** Check the full DEPLOYMENT_GUIDE.md or create an issue.

