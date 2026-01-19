#!/bin/bash

###############################################################################
# Deployment Script for Tendon Analysis Platform
# Usage: ./deploy.sh [production|staging]
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/app"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="tendon-analysis"

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run as root. Run as appuser."
        exit 1
    fi
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed"
        exit 1
    fi
    
    if ! command -v nginx &> /dev/null; then
        print_error "Nginx is not installed"
        exit 1
    fi
    
    if ! command -v redis-cli &> /dev/null; then
        print_error "Redis is not installed"
        exit 1
    fi
    
    print_success "All dependencies found"
}

setup_venv() {
    print_info "Setting up virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$APP_DIR/requirements.txt"
    print_success "Dependencies installed"
}

create_directories() {
    print_info "Creating required directories..."
    
    mkdir -p "$APP_DIR/uploads"
    mkdir -p "$APP_DIR/outputs"
    mkdir -p "$APP_DIR/logs"
    
    chmod 755 "$APP_DIR/uploads"
    chmod 755 "$APP_DIR/outputs"
    chmod 755 "$APP_DIR/logs"
    
    print_success "Directories created"
}

check_env_file() {
    print_info "Checking .env file..."
    
    if [ ! -f "$APP_DIR/.env" ]; then
        print_error ".env file not found!"
        print_info "Please create .env file from .env.example"
        exit 1
    fi
    
    # Check for required variables
    required_vars=("SECRET_KEY" "FLASK_ENV")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$APP_DIR/.env"; then
            print_error "Missing required variable: $var"
            exit 1
        fi
    done
    
    print_success ".env file configured"
}

restart_services() {
    print_info "Restarting services..."
    
    # Restart application
    sudo systemctl restart "$SERVICE_NAME"
    print_success "Application restarted"
    
    # Restart Nginx
    sudo systemctl restart nginx
    print_success "Nginx restarted"
    
    # Check status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Application is running"
    else
        print_error "Application failed to start"
        sudo journalctl -u "$SERVICE_NAME" -n 20
        exit 1
    fi
}

run_tests() {
    print_info "Running basic tests..."
    
    source "$VENV_DIR/bin/activate"
    
    # Test imports
    python3 -c "import flask; import cv2; import pandas; import torch" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Python imports successful"
    else
        print_error "Python import test failed"
        exit 1
    fi
    
    # Test Redis connection
    if redis-cli ping > /dev/null 2>&1; then
        print_success "Redis connection successful"
    else
        print_error "Redis connection failed"
        exit 1
    fi
}

show_status() {
    echo ""
    echo "=========================================="
    echo "Deployment Status"
    echo "=========================================="
    
    # Application status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Application: Running"
    else
        print_error "Application: Stopped"
    fi
    
    # Nginx status
    if sudo systemctl is-active --quiet nginx; then
        print_success "Nginx: Running"
    else
        print_error "Nginx: Stopped"
    fi
    
    # Redis status
    if sudo systemctl is-active --quiet redis; then
        print_success "Redis: Running"
    else
        print_error "Redis: Stopped"
    fi
    
    echo "=========================================="
}

# Main deployment flow
main() {
    echo "=========================================="
    echo "Tendon Analysis Platform - Deployment"
    echo "=========================================="
    echo ""
    
    check_root
    check_dependencies
    check_env_file
    create_directories
    setup_venv
    run_tests
    restart_services
    show_status
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    print_info "View logs: sudo journalctl -u $SERVICE_NAME -f"
    print_info "Application URL: http://$(hostname -I | awk '{print $1}')"
}

# Run main function
main "$@"

