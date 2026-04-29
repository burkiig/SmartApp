# ═══════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT CHECKLIST FOR SMARTAPP - RENDER CLOUD
# ═══════════════════════════════════════════════════════════════════════════════
#
# Before deploying to Render, verify all items are complete.
# Keep this document up to date and reference it before each deployment.

## PRE-DEPLOYMENT VERIFICATION

### Infrastructure & Security
- [ ] Render account created and verified
- [ ] GitHub repository connected to Render
- [ ] MongoDB database created on Render (or external)
- [ ] Environment variables prepared with secure values
- [ ] Domain name registered (optional, Render provides .onrender.com)
- [ ] SSL certificate will be auto-provisioned by Render
- [ ] CORS origins configured correctly
- [ ] Backup strategy defined (Render provides automated backups for paid DB)

### Code Quality
- [ ] All code reviewed and approved
- [ ] Security vulnerabilities scanned (npm audit, pip audit)
- [ ] No hardcoded secrets in codebase
- [ ] Environment variables properly referenced in code
- [ ] Build tested locally with Docker
- [ ] Unit tests passing (npm test, pytest)
- [ ] Integration tests passing
- [ ] Performance benchmarks acceptable
- [ ] Database migrations tested
- [ ] Rollback plan prepared (use Render's deployment history)

### Environment Configuration
- [ ] .env file created with development values
- [ ] SECRET_KEY set to strong random value (32+ characters)
- [ ] JWT_SECRET_KEY set to strong random value (32+ characters)
- [ ] DEBUG set to False for production
- [ ] FLASK_ENV set to production
- [ ] MONGODB_URI configured with Render database URL
- [ ] CORS_ORIGINS configured with production domains
- [ ] LOG_LEVEL appropriate for production (INFO or WARNING)
- [ ] All required environment variables documented
- [ ] No test/dummy values in production environment

### Dependencies & Requirements
- [ ] All Python dependencies specified in requirements.txt
- [ ] All Node.js dependencies specified in package.json
- [ ] No unnecessary development dependencies in production
- [ ] Versions pinned for reproducibility
- [ ] Dependencies regularly updated and scanned
- [ ] Docker build tested locally
- [ ] Compatibility matrix verified

### Database Preparation
- [ ] Database created and initialized
- [ ] Database user created with appropriate permissions
- [ ] Database connection tested
- [ ] Backup user configured
- [ ] Backup process tested
- [ ] Recovery procedure documented and tested
- [ ] Database indexes created
- [ ] Query performance optimized

### SSL/TLS Configuration
- [ ] SSL certificate installed and valid
- [ ] Certificate renewal automated (certbot)
- [ ] SSL protocols restricted to TLSv1.2+
- [ ] Strong ciphers configured
- [ ] HSTS enabled
- [ ] SSL certificate pinning considered
- [ ] Chain of trust verified

### Application Setup
- [ ] React web panel built for production
- [ ] Static files optimized and minified
- [ ] Asset hashing enabled for cache busting
- [ ] Source maps excluded from production
- [ ] Service worker registered for offline support
- [ ] Manifest.json properly configured
- [ ] Application version/build info tracked

### Nginx/Reverse Proxy
- [ ] Nginx configuration syntax validated
- [ ] All required location blocks configured
- [ ] SSL certificates referenced correctly
- [ ] Gzip compression enabled
- [ ] Cache headers configured appropriately
- [ ] Rate limiting configured
- [ ] Security headers set correctly
- [ ] Logging paths configured
- [ ] Buffer sizes optimized

### Gunicorn Configuration
- [ ] Worker count set appropriately (2*CPU + 1)
- [ ] Worker class appropriate for application
- [ ] Timeout values set correctly
- [ ] Keep-alive configured
- [ ] Max requests set to prevent memory leaks
- [ ] Access and error logs configured
- [ ] PID file location valid
- [ ] User/group permissions set

### Process Management
- [ ] Systemd service file created and enabled
- [ ] Service restart policy configured
- [ ] Service dependencies configured
- [ ] Resource limits set (memory, CPU)
- [ ] Security settings applied (ProtectSystem, etc.)
- [ ] Log rotation configured
- [ ] Log retention policies set

### Monitoring & Logging
- [ ] Application logs being collected
- [ ] Log rotation configured to prevent disk full
- [ ] Log aggregation configured (if centralized logging)
- [ ] Uptime monitoring configured
- [ ] Performance monitoring configured (CPU, Memory, Disk)
- [ ] Database monitoring configured
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Health check endpoint verified
- [ ] Alert thresholds configured

### Docker Deployment (if using containers)
- [ ] Dockerfile built and tested
- [ ] Base image verified and updated
- [ ] Non-root user implemented
- [ ] Health check implemented
- [ ] Resource limits configured
- [ ] Logging driver configured
- [ ] Volume mounts configured
- [ ] Network isolation configured
- [ ] docker-compose.yml configured correctly

### Backup & Recovery
- [ ] Backup script tested
- [ ] Backup location accessible and writable
- [ ] Backup retention policy configured
- [ ] Recovery procedure documented
- [ ] Full disaster recovery test completed
- [ ] Backup integrity verified
- [ ] Off-site backup copies configured
- [ ] Backup encryption implemented

### Performance Optimization
- [ ] Static assets cached (30+ days)
- [ ] HTML documents not cached
- [ ] Database indexes optimized
- [ ] Database query performance verified
- [ ] Application response times acceptable
- [ ] Asset minification and compression enabled
- [ ] CDN configured (if applicable)
- [ ] Cache invalidation strategy tested

### Security Hardening
- [ ] Firewall rules restrictive and tested
- [ ] SSH hardening applied (key auth only, non-standard port)
- [ ] Regular security updates scheduled
- [ ] Security patches applied to all components
- [ ] Unnecessary services disabled
- [ ] File permissions hardened
- [ ] Secrets properly managed (not in code, logs, or version control)
- [ ] CSRF protection enabled
- [ ] SQL injection protections verified
- [ ] XSS protection configured
- [ ] Security headers configured (CSP, X-Frame-Options, etc.)

### Documentation & Runbooks
- [ ] Deployment procedure documented
- [ ] Rollback procedure documented
- [ ] Troubleshooting guide created
- [ ] Architecture diagram created
- [ ] Data flow diagram created
- [ ] API documentation current
- [ ] Database schema documented
- [ ] Deployment team trained
- [ ] Escalation procedures defined

### Team & Access Control
- [ ] Team members trained on procedures
- [ ] Access control matrix defined
- [ ] SSH access restricted to specific team members
- [ ] Database access controlled and logged
- [ ] Code repository access configured
- [ ] Deployment access restricted
- [ ] Emergency access procedure defined

### Communication & Coordination
- [ ] Maintenance window scheduled and communicated
- [ ] Stakeholders notified of deployment
- [ ] Change log created
- [ ] Deployment impact assessed
- [ ] Rollback communication plan prepared
- [ ] Status page updated (if applicable)
- [ ] Support team briefed on changes

---

## DEPLOYMENT EXECUTION

### Day-of Deployment

1. **Pre-Deployment (T-30 minutes)**
   - [ ] All team members present and connected
   - [ ] Final health checks on staging environment
   - [ ] Database backup completed
   - [ ] Communication channels open (Slack, on-call, etc.)
   - [ ] Monitoring dashboards open
   - [ ] Rollback plan reviewed

2. **Deployment (T-0)**
   - [ ] Code deployed to production
   - [ ] Database migrations applied
   - [ ] Application restarted
   - [ ] Health checks passing
   - [ ] API endpoints responding
   - [ ] Static assets serving correctly
   - [ ] SSL/TLS working
   - [ ] Logs being written
   - [ ] No errors in application logs
   - [ ] No errors in Nginx logs

3. **Post-Deployment (T+15 minutes)**
   - [ ] Smoke tests completed
   - [ ] User-facing functionality verified
   - [ ] Performance metrics acceptable
   - [ ] Error rate normal
   - [ ] Database performing well
   - [ ] Backup completed successfully
   - [ ] All monitoring alerts green
   - [ ] Status page updated (if applicable)

4. **Post-Deployment Monitoring (T+1 hour)**
   - [ ] Continued monitoring of metrics
   - [ ] User reports checked
   - [ ] Database growth normal
   - [ ] No unusual errors
   - [ ] Performance stable
   - [ ] Ready to declare success

---

## POST-DEPLOYMENT

### Day 1-7
- [ ] Monitor application logs daily
- [ ] Check performance metrics daily
- [ ] Monitor error rates
- [ ] Review user feedback
- [ ] Monitor database size growth
- [ ] Verify backups completing successfully
- [ ] Document any issues and resolutions

### Week 1+
- [ ] Performance baseline established
- [ ] No unexpected errors
- [ ] User adoption monitoring
- [ ] Security scan completed
- [ ] Post-deployment retrospective scheduled

---

## ROLLBACK PROCEDURE

If critical issues are discovered:

1. **Declare Rollback**
   - [ ] Decision made within 15 minutes of detection
   - [ ] Stakeholders notified
   - [ ] Rollback plan activated

2. **Execute Rollback**
   - [ ] Previous version deployed
   - [ ] Database rolled back (if migrations applied)
   - [ ] Application restarted
   - [ ] Health checks verified

3. **Post-Rollback**
   - [ ] Communicate status to stakeholders
   - [ ] Monitor for issues
   - [ ] Root cause analysis initiated
   - [ ] Fix developed and tested
   - [ ] Re-deployment scheduled

---

## SIGN-OFF

- [ ] Deployment Lead: _________________ Date: _______
- [ ] Infrastructure: _________________ Date: _______
- [ ] QA Lead: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______

---

## NOTES

Use this space to document any special considerations or issues encountered:

_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________
