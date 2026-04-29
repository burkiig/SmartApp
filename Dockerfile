# ═══════════════════════════════════════════════════════════════════════════════
# Dockerfile for SmartApp - Production Ready
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Build: docker build -t smartapp:latest .
# Run: docker run -d --name smartapp -p 5000:5000 smartapp:latest

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Node.js build stage (React panel)
# ─────────────────────────────────────────────────────────────────────────────

FROM node:18-alpine AS react-builder

WORKDIR /app/web-panel

# Copy package files
COPY web-panel/package*.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy source
COPY web-panel/src ./src
COPY web-panel/public ./public
COPY web-panel/.env* ./
COPY web-panel/*.config.js ./

# Build production bundle
RUN npm run build

# Verify build
RUN test -d /app/web-panel/build || (echo "Build failed!" && exit 1)

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Python application stage
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.9-slim

LABEL maintainer="SmartApp Development Team"
LABEL description="Smart Attendance System - Production Image"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_HOME=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    curl \
    tini \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -r -s /bin/bash -u 1000 smartapp && \
    mkdir -p $APP_HOME && \
    chown -R smartapp:smartapp $APP_HOME

# Set working directory
WORKDIR $APP_HOME

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copy application code
COPY --chown=smartapp:smartapp . .

# Copy built React panel from builder stage
COPY --from=react-builder --chown=smartapp:smartapp /app/web-panel/build ./web-panel/build

# Create necessary directories
RUN mkdir -p /app/static/faces /app/static/attendance /app/logs && \
    chown -R smartapp:smartapp /app

# Switch to non-root user
USER smartapp

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use tini to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start Gunicorn
CMD ["gunicorn", "-c", "deployment/gunicorn_production.conf.py", "app:create_app()"]
