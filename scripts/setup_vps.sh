#!/bin/bash

###############################################################################
# VPS Initial Setup Script
# Run this on a fresh DigitalOcean Ubuntu 22.04 droplet
# Usage: curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/scripts/setup_vps.sh | bash
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_header "Tendon Analysis Platform - VPS Setup"

# Update system
print_info "Updating system packages..."
apt update && apt upgrade -y
print_success "System updated"

# Install dependencies
print_info "Installing system dependencies..."
apt install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    redis-server \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    supervisor \
    curl \
    wget \
    htop \
    ufw \
    certbot \
    python3-certbot-nginx
print_success "Dependencies installed"

# Create application user
print_info "Creating application user..."
if id "appuser" &>/dev/null; then
    print_info "User 'appuser' already exists"
else
    adduser --disabled-password --gecos "" appuser
    usermod -aG sudo appuser
    print_success "User 'appuser' created"
fi

# Setup firewall
print_info "Configuring firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 'Nginx Full'
print_success "Firewall configured"

# Configure Redis
print_info "Configuring Redis..."
sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis/redis.conf
sed -i 's/^# maxmemory .*/maxmemory 256mb/' /etc/redis/redis.conf
sed -i 's/^# maxmemory-policy .*/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
systemctl restart redis
systemctl enable redis
print_success "Redis configured"

# Create application directory
print_info "Creating application directory..."
mkdir -p /var/www/app
chown -R appuser:appuser /var/www/app
print_success "Application directory created"

# Setup log rotation
print_info "Configuring log rotation..."
cat > /etc/logrotate.d/tendon-analysis << 'EOF'
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
EOF
print_success "Log rotation configured"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

print_header "Setup Complete!"
echo ""
print_success "System is ready for application deployment"
echo ""
print_info "Next steps:"
echo "  1. Switch to appuser: su - appuser"
echo "  2. Upload application files to /var/www/app"
echo "  3. Run deployment script: cd /var/www/app && ./deploy.sh"
echo ""
print_info "Server IP: $SERVER_IP"
print_info "SSH: ssh appuser@$SERVER_IP"
echo ""
print_info "For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""

