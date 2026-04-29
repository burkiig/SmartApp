"""
Gunicorn Production Configuration for SmartApp
==============================================================================

Usage:
    gunicorn -c deployment/gunicorn_production.conf.py "app:create_app()"

Or with systemd service:
    [Service]
    ExecStart=/path/to/venv/bin/gunicorn -c /path/to/deployment/gunicorn_production.conf.py "app:create_app()"
"""

import os
import multiprocessing
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# SERVER SOCKET
# ─────────────────────────────────────────────────────────────────────────────

# Bind to local socket (use Nginx as reverse proxy)
# For Render deployment, bind to 0.0.0.0:PORT
port = os.environ.get('PORT', '5000')
bind = [
    f"0.0.0.0:{port}",
    # "unix:/tmp/smartapp.sock",  # Unix socket for better performance (disabled for Render)
]

# Backlog (pending connections queue)
backlog = 2048

# ─────────────────────────────────────────────────────────────────────────────
# WORKER PROCESSES
# ─────────────────────────────────────────────────────────────────────────────

# Number of worker processes
# Formula: (2 * CPU_CORES) + 1
workers = int(os.getenv("WORKERS", (multiprocessing.cpu_count() * 2) + 1))

# Worker class: sync, eventlet, gevent, tornado
worker_class = "sync"

# Worker timeout (seconds) - increase for long-running requests
timeout = int(os.getenv("WORKER_TIMEOUT", 120))

# Keep-alive timeout
keepalive = int(os.getenv("KEEPALIVE", 5))

# Max requests per worker (restart after N requests to prevent memory leaks)
max_requests = 1000

# Random jitter for max_requests to prevent thundering herd
max_requests_jitter = 50

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING & DEBUGGING
# ─────────────────────────────────────────────────────────────────────────────

# Access log format
accesslog = os.getenv("ACCESSLOG", "/var/log/smartapp/gunicorn_access.log")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Error log
errorlog = os.getenv("ERRORLOG", "/var/log/smartapp/gunicorn_error.log")
loglevel = os.getenv("LOG_LEVEL", "info")

# Silence healthcheck logs
silence_access_log_for_healthchecks = True

# ─────────────────────────────────────────────────────────────────────────────
# REQUEST HANDLING
# ─────────────────────────────────────────────────────────────────────────────

# Limit request line size
limit_request_line = 8190

# Limit request fields
limit_request_fields = 100

# Limit request field size
limit_request_field_size = 8190

# ─────────────────────────────────────────────────────────────────────────────
# SERVER MECHANICS
# ─────────────────────────────────────────────────────────────────────────────

# Preload application code before forking worker processes
preload_app = True

# Daemon mode (run in background)
daemon = False

# PID file
pidfile = "/var/run/smartapp/gunicorn.pid"

# User/Group (if running as root)
# user = "smartapp"
# group = "smartapp"

# Temporary directory for sockets
tmp_upload_dir = "/tmp"

# ─────────────────────────────────────────────────────────────────────────────
# PERFORMANCE TUNING
# ─────────────────────────────────────────────────────────────────────────────

# TCP Keep-Alive
tcp_keep_alive = 5

# Prevent connections from timing out too quickly
graceful_timeout = 30

# Reload configuration when changed
# reload_on_change = True  # Not recommended in production

# ─────────────────────────────────────────────────────────────────────────────
# DEPLOYMENT HOOKS
# ─────────────────────────────────────────────────────────────────────────────

def on_starting(server):
    """Called before any worker is spawned."""
    print("[Gunicorn] Starting SmartApp with {} workers".format(server.cfg.workers))
    
    # Ensure log directories exist
    os.makedirs("/var/log/smartapp", exist_ok=True)
    os.makedirs("/var/run/smartapp", exist_ok=True)

def when_ready(server):
    """Called after workers are spawned."""
    print("[Gunicorn] SmartApp ready. Listening on: {}".format(server.cfg.bind))

def on_exit(server):
    """Called when Gunicorn exits."""
    print("[Gunicorn] SmartApp shutting down")

def worker_int(worker):
    """Called when a worker is interrupted."""
    print(f"[Worker {worker.pid}] Interrupted")

def worker_abort(worker):
    """Called when a worker is aborted."""
    print(f"[Worker {worker.pid}] Aborted")

# ─────────────────────────────────────────────────────────────────────────────
# ENVIRONMENT VARIABLES
# ─────────────────────────────────────────────────────────────────────────────

# Load environment from .env.production
raw_env = [
    f"ENVIRONMENT={os.getenv('ENVIRONMENT', 'production')}",
    f"DEBUG={os.getenv('DEBUG', 'false')}",
    f"DB_DRIVER={os.getenv('DB_DRIVER', 'mongodb')}",
]

# ═════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT NOTES:
# ═════════════════════════════════════════════════════════════════════════════
# 
# 1. Create system user:
#    sudo useradd -r -s /bin/bash smartapp
#
# 2. Create directories:
#    sudo mkdir -p /var/log/smartapp /var/run/smartapp /var/lib/smartapp
#    sudo chown smartapp:smartapp /var/log/smartapp /var/run/smartapp /var/lib/smartapp
#
# 3. Create systemd service (/etc/systemd/system/smartapp.service):
#    [Unit]
#    Description=SmartApp Gunicorn Service
#    After=network.target
#
#    [Service]
#    Type=notify
#    User=smartapp
#    WorkingDirectory=/opt/smartapp
#    ExecStart=/opt/smartapp/venv/bin/gunicorn -c deployment/gunicorn_production.conf.py "app:create_app()"
#    ExecReload=/bin/kill -s HUP $MAINPID
#    KillMode=mixed
#    KillSignal=SIGQUIT
#
#    [Install]
#    WantedBy=multi-user.target
#
# 4. Enable and start service:
#    sudo systemctl daemon-reload
#    sudo systemctl enable smartapp
#    sudo systemctl start smartapp
#
# 5. Monitor logs:
#    journalctl -u smartapp -f
#    tail -f /var/log/smartapp/gunicorn_error.log
