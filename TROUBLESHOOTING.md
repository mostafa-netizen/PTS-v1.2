# Deployment Troubleshooting Guide

Common issues and solutions for production deployment.

---

## 🔍 Quick Diagnostics

### Check Everything at Once

```bash
# Run this first to get an overview
./scripts/monitor.sh status

# Check logs
./scripts/monitor.sh logs

# Check resources
./scripts/monitor.sh resources
```

---

## 🚨 Common Issues

### 1. Application Won't Start

**Symptoms:**
- `systemctl status tendon-analysis` shows "failed" or "inactive"
- Can't access application

**Diagnosis:**
```bash
# Check service status
sudo systemctl status tendon-analysis

# View detailed logs
sudo journalctl -u tendon-analysis -n 50

# Check if port is in use
sudo lsof -i :5001
```

**Common Causes & Fixes:**

#### Missing Dependencies
```bash
cd /var/www/app
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tendon-analysis
```

#### Permission Issues
```bash
sudo chown -R appuser:appuser /var/www/app
sudo chmod 755 /var/www/app/uploads
sudo chmod 755 /var/www/app/outputs
sudo systemctl restart tendon-analysis
```

#### Invalid .env File
```bash
# Check for syntax errors
cat /var/www/app/.env

# Verify required variables
grep -E "SECRET_KEY|FLASK_ENV" /var/www/app/.env

# Fix permissions
chmod 600 /var/www/app/.env
```

#### Port Already in Use
```bash
# Find what's using the port
sudo lsof -i :5001

# Kill the process
sudo kill -9 PID

# Or change port in .env
nano /var/www/app/.env
# Change SERVER_PORT=5002
```

---

### 2. 502 Bad Gateway (Nginx Error)

**Symptoms:**
- Browser shows "502 Bad Gateway"
- Nginx is running but can't reach application

**Diagnosis:**
```bash
# Check if application is running
sudo systemctl status tendon-analysis

# Check if Gunicorn is listening
sudo netstat -tlnp | grep 5001

# Check Nginx error log
tail -f /var/log/nginx/tendon_error.log
```

**Fixes:**

#### Application Not Running
```bash
sudo systemctl start tendon-analysis
sudo systemctl status tendon-analysis
```

#### Wrong Port in Nginx Config
```bash
# Check Nginx upstream
grep "server 127.0.0.1" /etc/nginx/sites-available/tendon-analysis

# Should match SERVER_PORT in .env
grep SERVER_PORT /var/www/app/.env

# Fix and restart
sudo nano /etc/nginx/sites-available/tendon-analysis
sudo nginx -t
sudo systemctl restart nginx
```

#### Firewall Blocking
```bash
# Check firewall
sudo ufw status

# Allow Nginx
sudo ufw allow 'Nginx Full'
```

---

### 3. File Upload Fails

**Symptoms:**
- Upload button doesn't work
- "File too large" error
- Upload times out

**Diagnosis:**
```bash
# Check upload directory
ls -la /var/www/app/uploads

# Check disk space
df -h

# Check Nginx config
grep client_max_body_size /etc/nginx/sites-available/tendon-analysis
```

**Fixes:**

#### Disk Full
```bash
# Clean up old files
./scripts/monitor.sh cleanup

# Check space
df -h
```

#### File Size Limit
```bash
# Increase Nginx limit
sudo nano /etc/nginx/sites-available/tendon-analysis
# Change: client_max_body_size 100M;

sudo nginx -t
sudo systemctl restart nginx
```

#### Permission Issues
```bash
sudo chown -R appuser:appuser /var/www/app/uploads
sudo chmod 755 /var/www/app/uploads
```

---

### 4. Processing Hangs or Times Out

**Symptoms:**
- Upload succeeds but processing never completes
- Progress bar stuck
- Request times out

**Diagnosis:**
```bash
# Check if process is running
ps aux | grep python

# Check CPU/memory
htop

# Check logs
tail -f /var/www/app/logs/gunicorn_error.log
```

**Fixes:**

#### Increase Timeout
```bash
# Gunicorn timeout
nano /var/www/app/gunicorn_config.py
# Change: timeout = 600

# Nginx timeout
sudo nano /etc/nginx/sites-available/tendon-analysis
# Add to location /api/upload:
# proxy_read_timeout 600s;

sudo systemctl restart tendon-analysis
sudo systemctl restart nginx
```

#### Out of Memory
```bash
# Check memory
free -h

# Reduce batch size
nano /var/www/app/.env
# Change: OCR_BATCH_SIZE=8

sudo systemctl restart tendon-analysis
```

#### RunPod Connection Issues
```bash
# Test RunPod connection
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.runpod.io/v1/user

# Check .env
grep RUNPOD /var/www/app/.env

# Disable RunPod temporarily
nano /var/www/app/.env
# Change: FORCE_RUNPOD=false

sudo systemctl restart tendon-analysis
```

---

### 5. Redis Connection Failed

**Symptoms:**
- "Redis connection refused" in logs
- Job queue not working

**Diagnosis:**
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping

# Check if listening
sudo netstat -tlnp | grep 6379
```

**Fixes:**

#### Redis Not Running
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

#### Wrong Redis Configuration
```bash
# Check Redis config
grep -E "bind|port" /etc/redis/redis.conf

# Should be:
# bind 127.0.0.1
# port 6379

# Restart Redis
sudo systemctl restart redis
```

---

### 6. SSL Certificate Issues

**Symptoms:**
- "Not Secure" warning in browser
- Certificate expired
- HTTPS not working

**Diagnosis:**
```bash
# Check certificate
sudo certbot certificates

# Test SSL
curl -I https://your-domain.com
```

**Fixes:**

#### Certificate Expired
```bash
# Renew certificate
sudo certbot renew

# Restart Nginx
sudo systemctl restart nginx
```

#### Certificate Not Found
```bash
# Get new certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

---

### 7. High Resource Usage

**Symptoms:**
- Server slow or unresponsive
- High CPU usage
- Out of memory errors

**Diagnosis:**
```bash
# Check resources
htop

# Check disk
df -h

# Check processes
ps aux --sort=-%mem | head
```

**Fixes:**

#### Too Many Workers
```bash
nano /var/www/app/gunicorn_config.py
# Reduce workers:
# workers = 2

sudo systemctl restart tendon-analysis
```

#### Memory Leak
```bash
# Restart application
sudo systemctl restart tendon-analysis

# Monitor memory
watch -n 5 'ps aux | grep gunicorn'
```

#### Disk Full
```bash
# Clean up
./scripts/monitor.sh cleanup

# Find large files
du -sh /var/www/app/* | sort -h
```

---

## 🔧 Advanced Debugging

### Enable Debug Logging

```bash
# Temporarily enable debug mode
nano /var/www/app/.env
# Change: DEBUG_MODE=true
# Change: LOG_LEVEL=DEBUG

sudo systemctl restart tendon-analysis

# View detailed logs
tail -f /var/www/app/logs/gunicorn_error.log
```

### Test Components Individually

```bash
# Test Python imports
cd /var/www/app
source venv/bin/activate
python3 -c "import flask; import cv2; import torch; print('OK')"

# Test Redis
redis-cli ping

# Test Nginx config
sudo nginx -t

# Test application directly
python3 app.py
# Then Ctrl+C
```

---

## 📞 Getting Help

### Collect Information

Before asking for help, collect:

```bash
# System info
uname -a
cat /etc/os-release

# Service status
sudo systemctl status tendon-analysis nginx redis

# Recent logs
sudo journalctl -u tendon-analysis -n 100 > logs.txt

# Resource usage
free -h
df -h
```

### Log Files to Check

1. **Application**: `sudo journalctl -u tendon-analysis`
2. **Gunicorn**: `/var/www/app/logs/gunicorn_error.log`
3. **Nginx**: `/var/log/nginx/tendon_error.log`
4. **System**: `/var/log/syslog`

---

## 🆘 Emergency Recovery

### Complete Reset

```bash
# Stop services
sudo systemctl stop tendon-analysis nginx

# Clear temporary files
rm -rf /var/www/app/uploads/*
rm -rf /var/www/app/outputs/*

# Restart services
sudo systemctl start redis
sudo systemctl start tendon-analysis
sudo systemctl start nginx

# Check status
./scripts/monitor.sh status
```

### Rollback Deployment

```bash
# Restore from backup
# (if you have backups)

# Or redeploy
cd /var/www/app
git pull  # or re-upload files
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tendon-analysis
```

---

**Still having issues?** Check the full DEPLOYMENT_GUIDE.md or create an issue with logs attached.

