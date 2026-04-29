#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SmartApp Deployment Script
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Usage: sudo ./deploy.sh
#
# This script automates the deployment process for SmartApp in production

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/smartapp"
APP_USER="smartapp"
APP_GROUP="smartapp"
VENV_DIR="${APP_DIR}/venv"
DEPLOY_LOG="/var/log/smartapp/deploy.log"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

log_command() {
    echo "[$( date '+%Y-%m-%d %H:%M:%S')] $@" >> "$DEPLOY_LOG"
    "$@" >> "$DEPLOY_LOG" 2>&1
}

# ─────────────────────────────────────────────────────────────────────────────
# Pre-flight Checks
# ─────────────────────────────────────────────────────────────────────────────

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
    print_success "Running as root"
    
    # Check if application directory exists
    if [ ! -d "$APP_DIR" ]; then
        print_error "Application directory not found: $APP_DIR"
        exit 1
    fi
    print_success "Application directory exists: $APP_DIR"
    
    # Check if smartapp user exists
    if ! id "$APP_USER" &>/dev/null; then
        print_warning "User '$APP_USER' does not exist, creating..."
        useradd -r -s /bin/bash "$APP_USER"
    fi
    print_success "User '$APP_USER' exists"
    
    # Check Python version
    if ! command -v python3.9 &> /dev/null; then
        print_error "Python 3.9 not found"
        exit 1
    fi
    print_success "Python 3.9 found"
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found"
        exit 1
    fi
    print_success "Node.js found: $(node --version)"
}

# ─────────────────────────────────────────────────────────────────────────────
# Setup Directories
# ─────────────────────────────────────────────────────────────────────────────

setup_directories() {
    print_header "Setting Up Directories"
    
    local dirs=(
        "/var/log/smartapp"
        "/var/run/smartapp"
        "/var/lib/smartapp/static/faces"
        "/var/lib/smartapp/static/attendance"
        "/var/lib/smartapp/backups"
        "/var/lib/smartapp/data"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        chown "$APP_USER:$APP_GROUP" "$dir"
        chmod 750 "$dir"
        print_success "Created: $dir"
    done
}

# ─────────────────────────────────────────────────────────────────────────────
# Setup Python Environment
# ─────────────────────────────────────────────────────────────────────────────

setup_python_env() {
    print_header "Setting Up Python Environment"
    
    # Create virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3.9 -m venv "$VENV_DIR"
        chown -R "$APP_USER:$APP_GROUP" "$VENV_DIR"
    fi
    print_success "Virtual environment ready"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    su - "$APP_USER" -c "$VENV_DIR/bin/pip install --upgrade pip setuptools wheel" >> "$DEPLOY_LOG" 2>&1
    print_success "Pip upgraded"
    
    # Install requirements
    print_info "Installing Python dependencies..."
    su - "$APP_USER" -c "$VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt" >> "$DEPLOY_LOG" 2>&1
    print_success "Python dependencies installed"
}

# ─────────────────────────────────────────────────────────────────────────────
# Build React Panel
# ─────────────────────────────────────────────────────────────────────────────

build_react_panel() {
    print_header "Building React Web Panel"
    
    cd "${APP_DIR}/web-panel"
    
    # Install npm dependencies
    print_info "Installing npm dependencies..."
    su - "$APP_USER" -c "cd ${APP_DIR}/web-panel && npm ci" >> "$DEPLOY_LOG" 2>&1
    print_success "npm dependencies installed"
    
    # Build production bundle
    print_info "Building production bundle..."
    su - "$APP_USER" -c "cd ${APP_DIR}/web-panel && npm run build" >> "$DEPLOY_LOG" 2>&1
    print_success "React panel built successfully"
    
    # Verify build
    if [ ! -d "${APP_DIR}/web-panel/build" ]; then
        print_error "Build directory not found after build"
        exit 1
    fi
    print_success "Build verification passed"
}

# ─────────────────────────────────────────────────────────────────────────────
# Configure Systemd Service
# ─────────────────────────────────────────────────────────────────────────────

setup_systemd_service() {
    print_header "Setting Up Systemd Service"
    
    # Copy service file
    cp "${APP_DIR}/deployment/smartapp.service" "/etc/systemd/system/smartapp.service"
    chown root:root "/etc/systemd/system/smartapp.service"
    chmod 644 "/etc/systemd/system/smartapp.service"
    print_success "Service file installed"
    
    # Reload systemd
    systemctl daemon-reload
    print_success "Systemd daemon reloaded"
    
    # Enable service
    systemctl enable smartapp
    print_success "Service enabled"
}

# ─────────────────────────────────────────────────────────────────────────────
# Setup Nginx
# ─────────────────────────────────────────────────────────────────────────────

setup_nginx() {
    print_header "Setting Up Nginx"
    
    if [ ! -f "/etc/nginx/sites-available/smartapp" ]; then
        cp "${APP_DIR}/deployment/nginx.conf" "/etc/nginx/sites-available/smartapp"
        print_success "Nginx config installed"
        
        # Disable default site
        rm -f "/etc/nginx/sites-enabled/default"
        
        # Enable smartapp site
        ln -sf "/etc/nginx/sites-available/smartapp" "/etc/nginx/sites-enabled/smartapp"
        print_success "Nginx site enabled"
    fi
    
    # Test Nginx configuration
    if nginx -t >> "$DEPLOY_LOG" 2>&1; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration is invalid"
        exit 1
    fi
    
    # Reload Nginx
    systemctl reload nginx
    print_success "Nginx reloaded"
}

# ─────────────────────────────────────────────────────────────────────────────
# Setup Backups
# ─────────────────────────────────────────────────────────────────────────────

setup_backups() {
    print_header "Setting Up Backup Script"
    
    cp "${APP_DIR}/deployment/backup-smartapp.sh" "/usr/local/bin/backup-smartapp.sh"
    chmod 755 "/usr/local/bin/backup-smartapp.sh"
    print_success "Backup script installed"
    
    # Add cron job (daily at 2 AM)
    if ! grep -q "backup-smartapp" /var/spool/cron/crontabs/root; then
        echo "0 2 * * * /usr/local/bin/backup-smartapp.sh" | crontab -
        print_success "Backup cron job added"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Configure Permissions
# ─────────────────────────────────────────────────────────────────────────────

configure_permissions() {
    print_header "Configuring Permissions"
    
    chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"
    chmod -R u+rX,g+rX,o-rwx "$APP_DIR"
    
    # Make shell scripts executable
    chmod +x "${APP_DIR}/deployment"/*.sh
    
    print_success "Permissions configured"
}

# ─────────────────────────────────────────────────────────────────────────────
# Test Deployment
# ─────────────────────────────────────────────────────────────────────────────

test_deployment() {
    print_header "Testing Deployment"
    
    # Start service
    print_info "Starting SmartApp service..."
    systemctl start smartapp
    sleep 3
    
    # Check service status
    if systemctl is-active --quiet smartapp; then
        print_success "SmartApp service is running"
    else
        print_error "SmartApp service failed to start"
        print_info "Check logs: journalctl -u smartapp -n 50"
        exit 1
    fi
    
    # Test API health endpoint
    print_info "Testing API health endpoint..."
    if curl -s http://127.0.0.1:5000/health | grep -q '"status"'; then
        print_success "API health endpoint responding"
    else
        print_warning "API health endpoint not responding yet (may be starting)"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Deployment Flow
# ─────────────────────────────────────────────────────────────────────────────

main() {
    print_header "SmartApp Production Deployment"
    print_info "Start time: $(date)"
    print_info "Log file: $DEPLOY_LOG"
    
    # Create log file
    mkdir -p "$(dirname "$DEPLOY_LOG")"
    touch "$DEPLOY_LOG"
    
    check_prerequisites
    setup_directories
    setup_python_env
    build_react_panel
    setup_systemd_service
    setup_nginx
    setup_backups
    configure_permissions
    test_deployment
    
    print_header "Deployment Complete!"
    print_success "SmartApp has been successfully deployed"
    print_info "Service management:"
    print_info "  Start:   systemctl start smartapp"
    print_info "  Stop:    systemctl stop smartapp"
    print_info "          systemctl restart smartapp"
    print_info "  Status:  systemctl status smartapp"
    print_info "  Logs:    journalctl -u smartapp -f"
    print_info "End time: $(date)"
}

# ─────────────────────────────────────────────────────────────────────────────
# Error Handler
# ─────────────────────────────────────────────────────────────────────────────

trap 'print_error "Deployment failed at line $LINENO"; exit 1' ERR

# Run main function
main "$@"
