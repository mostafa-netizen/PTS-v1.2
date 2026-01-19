# Production Deployment Checklist

Complete checklist for deploying the Tendon Analysis Platform to production.

---

## 📋 Pre-Deployment

### Accounts & Access
- [ ] DigitalOcean account created
- [ ] Payment method added to DigitalOcean
- [ ] RunPod.io account created (optional)
- [ ] Payment method added to RunPod (optional)
- [ ] Domain name registered (optional)
- [ ] DNS configured to point to droplet IP (optional)

### Local Preparation
- [ ] Application tested locally
- [ ] All dependencies listed in requirements.txt
- [ ] Environment variables documented
- [ ] Sensitive data removed from code
- [ ] .gitignore configured properly

---

## 🖥️ DigitalOcean VPS Setup

### Droplet Creation
- [ ] Droplet created (Ubuntu 22.04 LTS)
- [ ] Appropriate size selected (min 2GB RAM)
- [ ] SSH key added or password set
- [ ] Droplet IP address noted
- [ ] Firewall configured (ports 22, 80, 443)

### Initial Server Configuration
- [ ] SSH access verified
- [ ] System packages updated (`apt update && upgrade`)
- [ ] Application user created (`appuser`)
- [ ] UFW firewall enabled
- [ ] SSH key-based authentication configured
- [ ] Root login disabled (optional but recommended)

### System Dependencies
- [ ] Python 3.10+ installed
- [ ] pip and venv installed
- [ ] Nginx installed
- [ ] Redis installed
- [ ] Poppler-utils installed
- [ ] System libraries installed (libgl1-mesa-glx, libglib2.0-0)
- [ ] Supervisor installed (optional)
- [ ] Certbot installed (for SSL)

---

## 🚀 Application Deployment

### File Transfer
- [ ] Application files uploaded to `/var/www/app`
- [ ] Correct ownership set (`chown -R appuser:appuser`)
- [ ] Correct permissions set (755 for directories, 644 for files)

### Python Environment
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] pip upgraded
- [ ] All dependencies installed from requirements.txt
- [ ] No installation errors

### Configuration
- [ ] `.env` file created from `.env.production`
- [ ] `SECRET_KEY` generated and set (32+ characters)
- [ ] `FLASK_ENV` set to `production`
- [ ] `DEBUG_MODE` set to `false`
- [ ] Redis configuration verified
- [ ] RunPod credentials added (if using)
- [ ] File paths configured correctly
- [ ] `.env` file permissions set to 600

### Directory Structure
- [ ] `uploads/` directory created
- [ ] `outputs/` directory created
- [ ] `logs/` directory created
- [ ] Correct permissions on all directories (755)

### Testing
- [ ] Application starts without errors
- [ ] Can access application on port 5001
- [ ] File upload works
- [ ] Processing completes successfully
- [ ] Results are downloadable

---

## ⚙️ Production Services

### Gunicorn
- [ ] `gunicorn_config.py` created
- [ ] Worker count configured appropriately
- [ ] Timeout settings configured
- [ ] Log paths configured
- [ ] Gunicorn tested manually

### Systemd Service
- [ ] Service file created (`/etc/systemd/system/tendon-analysis.service`)
- [ ] Service file syntax correct
- [ ] Service enabled (`systemctl enable`)
- [ ] Service started (`systemctl start`)
- [ ] Service status verified (`systemctl status`)
- [ ] Service auto-starts on boot

### Redis
- [ ] Redis running
- [ ] Redis bound to localhost only
- [ ] Memory limit configured
- [ ] Persistence enabled
- [ ] Redis password set (optional but recommended)
- [ ] Redis auto-starts on boot

### Nginx
- [ ] Nginx configuration file created
- [ ] Server name configured (domain or IP)
- [ ] Upstream configured correctly
- [ ] Client max body size set (50M)
- [ ] Rate limiting configured
- [ ] Static file serving configured
- [ ] Configuration syntax tested (`nginx -t`)
- [ ] Site enabled (symlink created)
- [ ] Nginx restarted
- [ ] Can access application through Nginx

---

## 🔒 Security

### SSL/TLS (if using domain)
- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] Certificate auto-renewal configured
- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] SSL grade verified (ssllabs.com)

### Firewall
- [ ] UFW enabled
- [ ] SSH allowed (port 22)
- [ ] HTTP allowed (port 80)
- [ ] HTTPS allowed (port 443)
- [ ] All other ports blocked
- [ ] Firewall rules tested

### Application Security
- [ ] Debug mode disabled
- [ ] Secret key is random and secure
- [ ] File upload size limited
- [ ] File type validation enabled
- [ ] Rate limiting configured
- [ ] CORS configured properly
- [ ] Session cookies secure (if using HTTPS)

### System Security
- [ ] System packages up to date
- [ ] Automatic security updates enabled
- [ ] Root login disabled
- [ ] SSH key authentication only
- [ ] Fail2ban installed (optional)
- [ ] Regular backups configured

---

## 🎮 RunPod Integration (Optional)

### RunPod Setup
- [ ] RunPod account created
- [ ] GPU pod deployed OR serverless endpoint created
- [ ] API key obtained
- [ ] Endpoint ID obtained
- [ ] RunPod credentials added to `.env`
- [ ] `FORCE_RUNPOD` set appropriately

### Testing
- [ ] RunPod connection tested
- [ ] OCR processing works via RunPod
- [ ] Costs monitored
- [ ] Auto-scaling configured (serverless)

---

## 📊 Monitoring & Maintenance

### Log Management
- [ ] Log rotation configured
- [ ] Log files accessible
- [ ] Error logs monitored
- [ ] Access logs reviewed

### Automated Cleanup
- [ ] Cron job for old uploads (24 hours)
- [ ] Cron job for old outputs (7 days)
- [ ] Cron job for old logs (30 days)
- [ ] Disk space monitored

### Monitoring
- [ ] Service status monitoring
- [ ] Resource usage monitoring (CPU, RAM, disk)
- [ ] Error rate monitoring
- [ ] Uptime monitoring (optional - UptimeRobot, etc.)

### Backups
- [ ] Backup strategy defined
- [ ] Critical data backed up
- [ ] Backup restoration tested
- [ ] Automated backups configured (optional)

---

## ✅ Final Verification

### Functionality
- [ ] Homepage loads correctly
- [ ] File upload works
- [ ] Processing completes successfully
- [ ] Progress updates work
- [ ] Results display correctly
- [ ] File downloads work
- [ ] Excel export works

### Performance
- [ ] Response time acceptable
- [ ] Processing time reasonable
- [ ] No memory leaks
- [ ] No excessive CPU usage
- [ ] Concurrent requests handled

### Reliability
- [ ] Application survives restart
- [ ] Application survives server reboot
- [ ] Error handling works
- [ ] Logs are being written
- [ ] No critical errors in logs

---

## 📝 Documentation

- [ ] Deployment documented
- [ ] Configuration documented
- [ ] Credentials stored securely
- [ ] Team members have access
- [ ] Runbook created for common issues
- [ ] Contact information updated

---

## 🎯 Post-Deployment

### Immediate (First 24 Hours)
- [ ] Monitor logs for errors
- [ ] Test all functionality
- [ ] Verify SSL certificate
- [ ] Check resource usage
- [ ] Test from different locations

### First Week
- [ ] Monitor performance
- [ ] Review error logs daily
- [ ] Check disk usage
- [ ] Verify backups working
- [ ] Monitor costs (RunPod)

### Ongoing
- [ ] Weekly log review
- [ ] Monthly security updates
- [ ] Quarterly dependency updates
- [ ] Regular backup testing
- [ ] Cost optimization review

---

## 🆘 Emergency Contacts

```
Server IP: ___________________
Domain: ______________________
SSH User: ____________________
DigitalOcean Login: __________
RunPod Login: ________________
DNS Provider: ________________
```

---

## 📞 Support Resources

- **Documentation**: See DEPLOYMENT_GUIDE.md
- **Quick Start**: See DEPLOYMENT_QUICKSTART.md
- **Monitoring**: Run `./scripts/monitor.sh`
- **Logs**: `sudo journalctl -u tendon-analysis -f`

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Version**: _______________


