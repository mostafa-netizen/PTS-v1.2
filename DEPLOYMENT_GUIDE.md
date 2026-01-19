# VPS Deployment Guide - DigitalOcean + RunPod.io

Complete guide for deploying the Tendon Analysis Platform on DigitalOcean VPS with GPU processing on RunPod.io.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Part 1: DigitalOcean VPS Setup](#part-1-digitalocean-vps-setup)
4. [Part 2: RunPod.io GPU Setup](#part-2-runpodio-gpu-setup)
5. [Part 3: Application Deployment](#part-3-application-deployment)
6. [Part 4: Production Configuration](#part-4-production-configuration)
7. [Part 5: Monitoring & Maintenance](#part-5-monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  Nginx  │ (Reverse Proxy + SSL)
                    │  :80/443│
                    └────┬────┘
                         │
              ┌──────────▼──────────┐
              │   Flask App         │
              │   (Gunicorn)        │
              │   :5001             │
              └──┬──────────────┬───┘
                 │              │
        ┌────────▼────┐    ┌───▼──────────┐
        │   Redis     │    │  RunPod.io   │
        │   :6379     │    │  GPU Server  │
        │  (Queue)    │    │  (OCR)       │
        └─────────────┘    └──────────────┘
                 │
        ┌────────▼────────┐
        │  Local Storage  │
        │  /var/www/app   │
        └─────────────────┘
```

**Components:**
- **DigitalOcean VPS**: Web server, API, file storage
- **RunPod.io**: GPU processing for OCR (optional, cost-effective)
- **Redis**: Job queue and session management
- **Nginx**: Reverse proxy, SSL termination, static files
- **Gunicorn**: Production WSGI server

---

## ✅ Prerequisites

### Accounts Needed
- [ ] DigitalOcean account ([Sign up](https://www.digitalocean.com/))
- [ ] RunPod.io account ([Sign up](https://www.runpod.io/)) - Optional
- [ ] Domain name (optional, for SSL)

### Local Requirements
- SSH client
- Basic Linux/terminal knowledge

---

## 📦 Part 1: DigitalOcean VPS Setup

### Step 1.1: Create Droplet

1. **Log in to DigitalOcean**
2. **Create → Droplets**
3. **Choose Configuration:**

   | Setting | Recommended Value |
   |---------|------------------|
   | **Image** | Ubuntu 22.04 LTS x64 |
   | **Plan** | Basic |
   | **CPU** | Regular Intel - $12/mo (2GB RAM, 1 vCPU) |
   | **Datacenter** | Choose closest to your users |
   | **Authentication** | SSH Key (recommended) or Password |
   | **Hostname** | tendon-analysis-app |

4. **Click "Create Droplet"**
5. **Note the IP address** (e.g., `123.45.67.89`)

### Step 1.2: Initial Server Setup

**Connect to your server:**
```bash
ssh root@YOUR_DROPLET_IP
```

**Update system:**
```bash
apt update && apt upgrade -y
```

**Create application user:**
```bash
# Create user
adduser appuser
usermod -aG sudo appuser

# Switch to new user
su - appuser
```

**Install system dependencies:**
```bash
sudo apt install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    redis-server \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    supervisor
```

### Step 1.3: Setup Firewall

```bash
# Enable UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

---

## 🚀 Part 2: RunPod.io GPU Setup

### Step 2.1: Create RunPod Account

1. Go to [runpod.io](https://www.runpod.io/)
2. Sign up / Log in
3. Add payment method (pay-as-you-go)

### Step 2.2: Deploy GPU Pod

1. **Navigate to "Pods"**
2. **Click "Deploy"**
3. **Choose GPU:**
   - **Recommended**: RTX 3070/3080 ($0.20-$0.40/hour)
   - **Budget**: RTX 3060 ($0.15/hour)
   - **High-end**: A4000/A5000 ($0.50-$0.80/hour)

4. **Select Template**: PyTorch or Custom
5. **Configure:**
   - Container Disk: 20GB
   - Volume: 10GB (optional)
   - Expose HTTP Ports: 8000
6. **Deploy Pod**

### Step 2.3: Setup RunPod Endpoint

**Option A: Serverless Endpoint (Recommended for Production)**

1. Navigate to **"Serverless"** → **"Endpoints"**
2. Click **"New Endpoint"**
3. **Configure:**
   - Name: `tendon-ocr-processor`
   - GPU: RTX 3070 or better
   - Workers: 1-3 (auto-scale)
   - Max Workers: 5
   - Idle Timeout: 5 seconds

4. **Deploy Custom Handler** (see RunPod integration code below)

**Option B: Pod Endpoint (Simpler, Always-On)**

1. **SSH into your RunPod pod:**
   ```bash
   ssh root@YOUR_POD_IP -p YOUR_POD_PORT
   ```

2. **Install dependencies:**
   ```bash
   pip install torch torchvision python-doctr opencv-python numpy pandas flask
   ```

3. **Create API server** (create custom endpoint for OCR processing)

4. **Get API endpoint:**
   - Format: `https://YOUR_POD_ID-8000.proxy.runpod.net`
   - Save this URL for later

### Step 2.4: Get RunPod API Credentials

1. Go to **Settings** → **API Keys**
2. Click **"Create API Key"**
3. **Copy the key** (starts with `runpod-...`)
4. **Save securely** - you'll need this for `.env` file

---

## 🔧 Part 3: Application Deployment

### Step 3.1: Clone Repository

**On your DigitalOcean VPS:**

```bash
# Navigate to web directory
cd /var/www

# Clone your repository (or upload files via SCP)
sudo mkdir -p /var/www/app
sudo chown -R appuser:appuser /var/www/app

# Upload your application files
# Option 1: Git clone
# sudo git clone https://github.com/YOUR_USERNAME/tendon-analysis.git app

# Option 2: SCP from local machine
# scp -r /path/to/project-latest-update/* appuser@YOUR_DROPLET_IP:/var/www/app/

# Navigate to app
cd /var/www/app
```

### Step 3.2: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3.3: Configure Environment Variables

**Create `.env` file:**

```bash
nano .env
```

**Add configuration:**

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=CHANGE_THIS_TO_RANDOM_STRING_MIN_32_CHARS
DEBUG_MODE=false

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5001

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# RunPod Configuration (GPU Processing)
RUNPOD_API_KEY=your-runpod-api-key-here
RUNPOD_ENDPOINT_ID=your-endpoint-id-here
FORCE_RUNPOD=true

# Storage Configuration
STORAGE_BACKEND=local
OUTPUT_FOLDER=/var/www/app/outputs
UPLOAD_FOLDER=/var/www/app/uploads

# Processing Configuration
PDF_DPI=200
OCR_BATCH_SIZE=24
MAX_CONCURRENT_JOBS=3
TILE_SIZE=1000
TILE_OVERLAP=250
```

**Generate secure secret key:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Set permissions:**

```bash
chmod 600 .env
```

### Step 3.4: Create Required Directories

```bash
mkdir -p uploads outputs logs
chmod 755 uploads outputs logs
```

### Step 3.5: Test Application

```bash
# Activate virtual environment
source venv/bin/activate

# Test run
python3 app.py
```

**Expected output:**
```
🚀 Starting Tendon Analysis Platform
Server: http://0.0.0.0:5001
GPU Enabled: False
Debug Mode: False
```

**Test in browser:** `http://YOUR_DROPLET_IP:5001`

Press `Ctrl+C` to stop.

---

## ⚙️ Part 4: Production Configuration

### Step 4.1: Setup Gunicorn

**Create Gunicorn config:**

```bash
nano /var/www/app/gunicorn_config.py
```

**Add:**

```python
import multiprocessing

# Server socket
bind = "127.0.0.1:5001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2

# Logging
accesslog = "/var/www/app/logs/gunicorn_access.log"
errorlog = "/var/www/app/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "tendon_analysis"

# Server mechanics
daemon = False
pidfile = "/var/www/app/gunicorn.pid"
user = "appuser"
group = "appuser"
tmp_upload_dir = None
```

### Step 4.2: Setup Systemd Service

**Create service file:**

```bash
sudo nano /etc/systemd/system/tendon-analysis.service
```

**Add:**

```ini
[Unit]
Description=Tendon Analysis Platform
After=network.target redis.service

[Service]
Type=notify
User=appuser
Group=appuser
WorkingDirectory=/var/www/app
Environment="PATH=/var/www/app/venv/bin"
ExecStart=/var/www/app/venv/bin/gunicorn \
    --config /var/www/app/gunicorn_config.py \
    app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable tendon-analysis
sudo systemctl start tendon-analysis
sudo systemctl status tendon-analysis
```

### Step 4.3: Setup Redis

**Configure Redis:**

```bash
sudo nano /etc/redis/redis.conf
```

**Update these settings:**

```conf
# Bind to localhost only
bind 127.0.0.1

# Set max memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Enable persistence
save 900 1
save 300 10
save 60 10000

# Set password (optional but recommended)
# requirepass YOUR_STRONG_PASSWORD
```

**Restart Redis:**

```bash
sudo systemctl restart redis
sudo systemctl enable redis
```

### Step 4.4: Setup Nginx

**Create Nginx config:**

```bash
sudo nano /etc/nginx/sites-available/tendon-analysis
```

**Add:**

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/m;

# Upstream application server
upstream app_server {
    server 127.0.0.1:5001 fail_timeout=0;
}

server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    client_max_body_size 50M;

    # Logging
    access_log /var/log/nginx/tendon_access.log;
    error_log /var/log/nginx/tendon_error.log;

    # Static files
    location /outputs/ {
        alias /var/www/app/outputs/;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }

    # Upload endpoint with rate limiting
    location /api/upload {
        limit_req zone=upload_limit burst=2 nodelay;
        proxy_pass http://app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api_limit burst=10 nodelay;
        proxy_pass http://app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Main application
    location / {
        proxy_pass http://app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/tendon-analysis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 4.5: Setup SSL with Let's Encrypt (Optional but Recommended)

**Install Certbot:**

```bash
sudo apt install certbot python3-certbot-nginx -y
```

**Get SSL certificate:**

```bash
sudo certbot --nginx -d your-domain.com
```

**Auto-renewal:**

```bash
sudo certbot renew --dry-run
```

---

## 📊 Part 5: Monitoring & Maintenance

### Step 5.1: Setup Log Rotation

**Create logrotate config:**

```bash
sudo nano /etc/logrotate.d/tendon-analysis
```

**Add:**

```conf
/var/www/app/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 appuser appuser
    sharedscripts
    postrotate
        systemctl reload tendon-analysis > /dev/null 2>&1 || true
    endscript
}
```

### Step 5.2: Setup File Cleanup Cron Job

**Edit crontab:**

```bash
crontab -e
```

**Add:**

```bash
# Delete uploads older than 24 hours
0 2 * * * find /var/www/app/uploads -type f -mtime +1 -delete

# Delete outputs older than 7 days
0 3 * * * find /var/www/app/outputs -type d -mtime +7 -exec rm -rf {} +

# Clean up old logs
0 4 * * * find /var/www/app/logs -name "*.log.*" -mtime +30 -delete
```

### Step 5.3: Monitoring Commands

**Check application status:**

```bash
# Service status
sudo systemctl status tendon-analysis

# View logs
sudo journalctl -u tendon-analysis -f

# Gunicorn logs
tail -f /var/www/app/logs/gunicorn_error.log
tail -f /var/www/app/logs/gunicorn_access.log

# Nginx logs
tail -f /var/log/nginx/tendon_error.log
tail -f /var/log/nginx/tendon_access.log
```

**Check resource usage:**

```bash
# CPU and memory
htop

# Disk usage
df -h
du -sh /var/www/app/*

# Redis status
redis-cli info
```

**Restart services:**

```bash
# Restart application
sudo systemctl restart tendon-analysis

# Restart Nginx
sudo systemctl restart nginx

# Restart Redis
sudo systemctl restart redis
```

---

## 🐛 Troubleshooting

### Issue: Application won't start

**Check logs:**
```bash
sudo journalctl -u tendon-analysis -n 50
```

**Common fixes:**
```bash
# Check permissions
sudo chown -R appuser:appuser /var/www/app

# Check virtual environment
source /var/www/app/venv/bin/activate
pip install -r requirements.txt

# Check port availability
sudo lsof -i :5001
```

### Issue: 502 Bad Gateway

**Causes:**
- Application not running
- Gunicorn not binding to correct port
- Firewall blocking connection

**Fix:**
```bash
# Check if app is running
sudo systemctl status tendon-analysis

# Check Gunicorn binding
sudo netstat -tlnp | grep 5001

# Restart services
sudo systemctl restart tendon-analysis
sudo systemctl restart nginx
```

### Issue: Upload fails

**Check:**
```bash
# File size limit in Nginx
grep client_max_body_size /etc/nginx/sites-available/tendon-analysis

# Disk space
df -h

# Permissions
ls -la /var/www/app/uploads
```

### Issue: Slow processing

**Optimize:**
```bash
# Check if RunPod is configured
cat /var/www/app/.env | grep RUNPOD

# Increase workers
nano /var/www/app/gunicorn_config.py
# Increase workers count

# Check Redis
redis-cli ping
```

### Issue: RunPod connection fails

**Debug:**
```bash
# Test API key
curl -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
     https://api.runpod.io/v1/user

# Check endpoint
cat /var/www/app/.env | grep RUNPOD_ENDPOINT_ID

# View application logs
tail -f /var/www/app/logs/gunicorn_error.log
```

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] DigitalOcean droplet created
- [ ] Domain name configured (optional)
- [ ] RunPod account created
- [ ] RunPod GPU pod deployed
- [ ] RunPod API key obtained

### Server Setup
- [ ] System updated
- [ ] User created
- [ ] Firewall configured
- [ ] Dependencies installed
- [ ] Application files uploaded

### Application Setup
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Directories created
- [ ] Application tested

### Production Configuration
- [ ] Gunicorn configured
- [ ] Systemd service created
- [ ] Redis configured
- [ ] Nginx configured
- [ ] SSL certificate installed (optional)

### Monitoring
- [ ] Log rotation configured
- [ ] Cleanup cron jobs created
- [ ] Monitoring commands tested

### Final Testing
- [ ] Application accessible via domain/IP
- [ ] File upload works
- [ ] Processing completes successfully
- [ ] Results downloadable
- [ ] SSL working (if configured)

---

## 🎯 Quick Commands Reference

```bash
# Application Management
sudo systemctl start tendon-analysis
sudo systemctl stop tendon-analysis
sudo systemctl restart tendon-analysis
sudo systemctl status tendon-analysis

# View Logs
sudo journalctl -u tendon-analysis -f
tail -f /var/www/app/logs/gunicorn_error.log

# Update Application
cd /var/www/app
git pull  # or upload new files
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tendon-analysis

# Nginx
sudo nginx -t
sudo systemctl restart nginx

# Redis
redis-cli ping
sudo systemctl restart redis

# Disk Cleanup
find /var/www/app/uploads -type f -mtime +1 -delete
find /var/www/app/outputs -type d -mtime +7 -exec rm -rf {} +
```

---

## 💰 Cost Estimation

### DigitalOcean VPS
- **Basic Droplet**: $12/month (2GB RAM, 1 vCPU)
- **Recommended**: $18/month (2GB RAM, 2 vCPU)
- **High Traffic**: $48/month (8GB RAM, 4 vCPU)

### RunPod.io GPU
- **Pay-as-you-go**: $0.15-$0.40/hour
- **Estimated usage**: 10 hours/month = $1.50-$4.00/month
- **Heavy usage**: 100 hours/month = $15-$40/month

### Total Monthly Cost
- **Light usage**: ~$15/month
- **Medium usage**: ~$25/month
- **Heavy usage**: ~$60/month

---

## 🚀 Next Steps

1. **Test thoroughly** with sample PDFs
2. **Monitor performance** for first week
3. **Optimize** based on usage patterns
4. **Setup backups** for critical data
5. **Consider** adding authentication
6. **Scale** as needed (more workers, bigger droplet)

---

**Your application is now deployed and ready for production! 🎉**

For support or questions, refer to the main README.md or create an issue in the repository.

