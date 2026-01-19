#!/bin/bash

###############################################################################
# Monitoring Script for Tendon Analysis Platform
# Usage: ./monitor.sh [status|logs|resources|cleanup]
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="tendon-analysis"
APP_DIR="/var/www/app"

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

check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        print_success "$service: Running"
        return 0
    else
        print_error "$service: Stopped"
        return 1
    fi
}

show_status() {
    print_header "Service Status"
    
    check_service "$SERVICE_NAME"
    check_service "nginx"
    check_service "redis"
    
    echo ""
    print_header "Application Info"
    
    # Get process info
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        PID=$(systemctl show -p MainPID --value "$SERVICE_NAME")
        if [ "$PID" != "0" ]; then
            MEM=$(ps -p "$PID" -o rss= | awk '{printf "%.1f MB", $1/1024}')
            CPU=$(ps -p "$PID" -o %cpu= | awk '{printf "%.1f%%", $1}')
            echo "PID: $PID"
            echo "Memory: $MEM"
            echo "CPU: $CPU"
        fi
    fi
    
    echo ""
    print_header "Disk Usage"
    df -h "$APP_DIR" | tail -n 1
    echo ""
    echo "Uploads: $(du -sh $APP_DIR/uploads 2>/dev/null | cut -f1)"
    echo "Outputs: $(du -sh $APP_DIR/outputs 2>/dev/null | cut -f1)"
    echo "Logs: $(du -sh $APP_DIR/logs 2>/dev/null | cut -f1)"
}

show_logs() {
    print_header "Recent Logs"
    
    echo ""
    print_info "Application Logs (last 20 lines):"
    sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    
    echo ""
    print_info "Gunicorn Error Log (last 10 lines):"
    if [ -f "$APP_DIR/logs/gunicorn_error.log" ]; then
        tail -n 10 "$APP_DIR/logs/gunicorn_error.log"
    else
        echo "No error log found"
    fi
}

show_resources() {
    print_header "System Resources"
    
    echo ""
    print_info "CPU & Memory:"
    top -bn1 | head -n 5
    
    echo ""
    print_info "Disk Usage:"
    df -h
    
    echo ""
    print_info "Memory Usage:"
    free -h
    
    echo ""
    print_info "Redis Info:"
    redis-cli info stats | grep -E "total_connections_received|total_commands_processed|keyspace"
    
    echo ""
    print_info "Network Connections:"
    netstat -an | grep -E ":5001|:80|:443" | wc -l
    echo "Active connections"
}

cleanup_files() {
    print_header "Cleanup"
    
    print_info "Cleaning up old files..."
    
    # Count files before
    UPLOADS_BEFORE=$(find "$APP_DIR/uploads" -type f 2>/dev/null | wc -l)
    OUTPUTS_BEFORE=$(find "$APP_DIR/outputs" -type d -mindepth 1 2>/dev/null | wc -l)
    
    # Delete old uploads (older than 1 day)
    find "$APP_DIR/uploads" -type f -mtime +1 -delete 2>/dev/null
    
    # Delete old outputs (older than 7 days)
    find "$APP_DIR/outputs" -type d -mindepth 1 -mtime +7 -exec rm -rf {} + 2>/dev/null
    
    # Delete old logs (older than 30 days)
    find "$APP_DIR/logs" -name "*.log.*" -mtime +30 -delete 2>/dev/null
    
    # Count files after
    UPLOADS_AFTER=$(find "$APP_DIR/uploads" -type f 2>/dev/null | wc -l)
    OUTPUTS_AFTER=$(find "$APP_DIR/outputs" -type d -mindepth 1 2>/dev/null | wc -l)
    
    print_success "Deleted $((UPLOADS_BEFORE - UPLOADS_AFTER)) upload files"
    print_success "Deleted $((OUTPUTS_BEFORE - OUTPUTS_AFTER)) output directories"
    
    echo ""
    print_info "Current disk usage:"
    df -h "$APP_DIR" | tail -n 1
}

tail_logs() {
    print_header "Live Logs (Ctrl+C to exit)"
    echo ""
    sudo journalctl -u "$SERVICE_NAME" -f
}

show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status      Show service status and basic info"
    echo "  logs        Show recent logs"
    echo "  tail        Follow live logs"
    echo "  resources   Show system resource usage"
    echo "  cleanup     Clean up old files"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 logs"
    echo "  $0 cleanup"
}

# Main
case "${1:-status}" in
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    tail)
        tail_logs
        ;;
    resources)
        show_resources
        ;;
    cleanup)
        cleanup_files
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

