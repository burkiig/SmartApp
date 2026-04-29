# ═══════════════════════════════════════════════════════════════════════════════
# SMARTAPP DEPLOYMENT GUIDE - RENDER CLOUD
# ═══════════════════════════════════════════════════════════════════════════════
#
# This guide covers deployment to Render cloud platform with:
# - Docker containerization
# - Managed MongoDB database
# - Automatic SSL certificates
# - Built-in monitoring and logging
# - Easy scaling

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Render Account Setup](#render-account-setup)
3. [Database Setup](#database-setup)
4. [Web Service Deployment](#web-service-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Domain Configuration](#domain-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

- [ ] GitHub repository created and code pushed
- [ ] Render account created (https://render.com)
- [ ] Domain name registered (optional, Render provides .onrender.com)
- [ ] Environment variables prepared
- [ ] Database schema migrations tested
- [ ] Application tested locally with Docker

---

## Render Account Setup

### 1. Create Render Account

1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub account for automatic deployments
3. Verify your email address

### 2. Connect Repository

1. In Render dashboard, click "New" → "Web Service"
2. Connect your GitHub repository containing SmartApp
3. Select the main branch (usually `main` or `master`)

---

## Database Setup

### 1. Create MongoDB Database

1. In Render dashboard, click "New" → "MongoDB"
2. Choose a name (e.g., `smartapp-db`)
3. Select plan (Free tier available)
4. Choose region closest to your users
5. Click "Create Database"

### 2. Get Connection Details

After creation, note the connection string from the "Connections" tab:
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

---

## Web Service Deployment

### 1. Create Web Service

1. Click "New" → "Web Service" in Render dashboard
2. Connect your GitHub repo
3. Configure the service:

**Service Settings:**
- **Name:** smartapp-backend (or your choice)
- **Environment:** Docker
- **Region:** Same as your database
- **Branch:** main (or your deployment branch)
- **Root Directory:** SmartApp (if your code is in a subdirectory)
- **Dockerfile Path:** Dockerfile (relative to root directory)

**Build & Deploy:**
- **Docker Command:** (leave default)
- **Health Check Path:** /health

### 2. Environment Variables

Add the following environment variables in the "Environment" tab:

```
# Flask Configuration
SECRET_KEY=<strong-random-key-32-chars>
JWT_SECRET_KEY=<strong-random-key-32-chars>
FLASK_ENV=production
DEBUG=False

# Database
MONGODB_URI=<your-mongodb-connection-string>

# CORS (update with your domain)
CORS_ORIGINS=https://yourdomain.com,https://smartapp-backend.onrender.com

# Logging
LOG_LEVEL=INFO

# Gunicorn
WORKERS=2
WORKER_TIMEOUT=120
```

### 3. Deploy

1. Click "Create Web Service"
2. Render will build and deploy your application
3. Monitor the build logs for any errors

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://...` |
| `CORS_ORIGINS` | Allowed origins | `https://yourdomain.com` |
| `FLASK_ENV` | Environment | `production` |
| `DEBUG` | Debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Generating Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY  
openssl rand -hex 32
```

---

## Domain Configuration

### Using Custom Domain (Optional)

1. In your Web Service settings, go to "Settings" tab
2. Add your custom domain in "Custom Domains"
3. Update DNS records as instructed by Render
4. Render will provision SSL certificate automatically

### Default Render Domain

Your app will be available at: `https://smartapp-backend.onrender.com`

---

## Monitoring & Maintenance

### Built-in Monitoring

Render provides:
- **Logs:** View application logs in real-time
- **Metrics:** CPU, memory, and response time graphs
- **Health Checks:** Automatic health monitoring
- **Auto-scaling:** Scale instances based on load (paid plans)

### Manual Monitoring

```bash
# Check application health
curl https://your-app.onrender.com/health

# View recent logs
# Use Render dashboard → Service → Logs tab
```

### Updates and Rollbacks

- **Automatic Deployments:** Push to main branch triggers deployment
- **Manual Deploy:** Click "Manual Deploy" in dashboard
- **Rollback:** Select previous deployment from "Deploys" tab

---

## Troubleshooting

### Common Issues

**Build Failures:**
- Check Dockerfile syntax
- Ensure all dependencies are in requirements.txt
- Verify Node.js build process

**Runtime Errors:**
- Check environment variables are set correctly
- Verify MongoDB connection string
- Review application logs

**Database Connection:**
- Ensure MongoDB is running
- Check connection string format
- Verify network access

### Getting Help

- **Render Docs:** https://docs.render.com/
- **Community:** https://community.render.com/
- **Support:** support@render.com

---

### 3. Connection Pooling

Already configured in Gunicorn with:
- Worker keep-alive connections
- Unix socket for local communication

---

## Deployment Verification Checklist

```bash
# 1. Service is running
sudo systemctl status smartapp

# 2. Nginx is serving correctly
curl -I https://yourdomain.com

# 3. API is responding
curl -s https://yourdomain.com/health | jq

# 4. Static files are served
curl -I https://yourdomain.com/index.html

# 5. Database connection works
curl -s https://yourdomain.com/api/health | jq .database

# 6. SSL certificate is valid
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | \
    openssl x509 -noout -dates

# 7. Backups are being created
ls -lh /var/lib/smartapp/backups/

# 8. Logs are being written
tail -f /var/log/smartapp/gunicorn_error.log
```

---

## Additional Resources

- [Gunicorn Docs](https://docs.gunicorn.org/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [MongoDB Docs](https://docs.mongodb.com/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
