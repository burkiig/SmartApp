# ═══════════════════════════════════════════════════════════════════════════════
# SECURITY HARDENING GUIDE FOR SMARTAPP
# ═══════════════════════════════════════════════════════════════════════════════

## Table of Contents
1. [Application Security](#application-security)
2. [Network Security](#network-security)
3. [Database Security](#database-security)
4. [Infrastructure Security](#infrastructure-security)
5. [Monitoring & Auditing](#monitoring--auditing)
6. [Incident Response](#incident-response)

---

## Application Security

### 1. Environment Variables & Secrets Management

**Never commit secrets to version control!**

```bash
# Use environment variables
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Store in secure location
sudo nano /opt/smartapp/.env
```

### 2. Authentication & Authorization

- [ ] Enable JWT authentication for API endpoints
- [ ] Implement role-based access control (RBAC)
- [ ] Use strong password requirements
- [ ] Hash passwords with bcrypt or similar
- [ ] Implement rate limiting on login attempts
- [ ] Set appropriate JWT expiration times (1 hour access, 30 days refresh)
- [ ] Implement refresh token rotation
- [ ] Validate and sanitize all user inputs

### 3. Input Validation

```python
# Always validate input
from werkzeug.security import safe_str_cmp
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(user_input):
    # Remove dangerous characters
    return user_input.strip()[:255]
```

### 4. SQL Injection Prevention

- [ ] Use parameterized queries (prepared statements)
- [ ] Use ORM frameworks (SQLAlchemy)
- [ ] Validate and escape all user input
- [ ] Use whitelist validation for database operations

### 5. Cross-Site Scripting (XSS) Prevention

- [ ] Enable Content-Security-Policy headers
- [ ] Escape all user-generated content
- [ ] Use templating engines that auto-escape
- [ ] Validate and sanitize file uploads

### 6. Cross-Site Request Forgery (CSRF) Prevention

- [ ] Implement CSRF tokens
- [ ] Use SameSite cookie flag
- [ ] Validate Origin/Referer headers

### 7. File Upload Security

```python
# Secure file handling
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(file):
    if file.size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    filename = secure_filename(file.filename)
    
    # Generate random name to prevent directory traversal
    random_name = os.urandom(16).hex() + os.path.splitext(filename)[1]
    
    # Store in secure location
    filepath = os.path.join(UPLOAD_DIR, random_name)
    file.save(filepath)
    
    return filepath
```

### 8. API Security

- [ ] Use HTTPS/TLS for all API communication
- [ ] Implement API rate limiting (10 req/s per IP)
- [ ] Validate API tokens on every request
- [ ] Log all API access
- [ ] Implement request/response size limits
- [ ] Use API versioning
- [ ] Implement request signing for sensitive operations

### 9. Session Management

- [ ] Use secure session cookies (HttpOnly, Secure, SameSite)
- [ ] Implement session timeout (15-30 minutes)
- [ ] Regenerate session IDs after login
- [ ] Implement logout (invalidate session)
- [ ] Use secure cookie names (avoid predictable)

```python
# Secure session configuration
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 1800  # 30 minutes
```

### 10. Logging & Error Handling

```python
# Never log sensitive information
import logging

logger = logging.getLogger(__name__)

# Good
logger.info(f"User {user_id} logged in successfully")

# Bad - never do this!
# logger.error(f"Password mismatch for {password}")  # DON'T LOG PASSWORDS

# Mask sensitive data in logs
def mask_sensitive_data(data):
    if 'password' in data:
        data['password'] = '***MASKED***'
    if 'token' in data:
        data['token'] = '***MASKED***'
    return data
```

---

## Network Security

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# SSH access (restrict to specific IPs if possible)
sudo ufw allow from 192.168.1.0/24 to any port 22

# HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# MySQL (if not local)
# sudo ufw allow from 192.168.1.5 to any port 3306

# Verify
sudo ufw status
```

### 2. SSH Hardening

**File: `/etc/ssh/sshd_config`**

```bash
# Disable root login
PermitRootLogin no

# Disable password authentication
PasswordAuthentication no

# Enable public key authentication
PubkeyAuthentication yes

# Use non-standard port (optional)
Port 22222

# Limit connection attempts
MaxAuthTries 3
MaxSessions 5

# Disable X11 forwarding if not needed
X11Forwarding no

# Remove less secure algorithms
HostKey /etc/ssh/ssh_host_ed25519_key
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org
Ciphers aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Restart SSH
sudo systemctl restart ssh
```

### 3. TLS/SSL Configuration

```nginx
# Nginx SSL hardening already in nginx.conf:
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;

# Test SSL/TLS
curl -I --tlsv1.2 https://yourdomain.com
```

### 4. Network Segmentation

- [ ] Isolate database server in separate subnet
- [ ] Use VPC security groups to restrict traffic
- [ ] Implement network segmentation for microservices
- [ ] Use private subnets for internal services

---

## Database Security

### 1. MongoDB Security

```javascript
// Create least-privileged user
db.createUser({
  user: 'smartapp_user',
  pwd: 'strong-random-password-here',
  roles: [
    { role: 'dbOwner', db: 'smart_attendance_prod' }
  ]
})

// Enable authentication
// Edit /etc/mongod.conf:
// security:
//   authorization: enabled

// Restart MongoDB
sudo systemctl restart mongod
```

### 2. Database Encryption

```bash
# MongoDB Enterprise - enable encryption at rest
# Edit /etc/mongod.conf:
# security:
#   encryptionAtRest:
#     engine: wiredTiger
#     keyFile: /etc/mongodb/encryption.key

# For SQLite - use encrypted database (SQLCipher)
```

### 3. Database Backup Security

- [ ] Encrypt all backups
- [ ] Store backups securely
- [ ] Test backup restoration regularly
- [ ] Restrict backup access to authorized personnel
- [ ] Use separate credentials for backup user

```bash
# Encrypted backup
mongodump --archive=/path/to/backup.archive \
          --username smartapp_user \
          --password "password" \
          --authenticationDatabase admin | \
          openssl enc -aes-256-cbc -salt -out /path/to/backup.archive.enc

# Restore from encrypted backup
openssl enc -d -aes-256-cbc -in /path/to/backup.archive.enc | \
        mongorestore --archive
```

### 4. Database Access Control

- [ ] Use connection strings with credentials
- [ ] Implement database-level authentication
- [ ] Audit all database access
- [ ] Restrict database access by IP address
- [ ] Disable unnecessary database features

---

## Infrastructure Security

### 1. Operating System Hardening

```bash
# Install and enable UFW
sudo apt-get install ufw
sudo ufw enable

# Update and patch system
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade

# Disable unnecessary services
sudo systemctl disable avahi-daemon
sudo systemctl disable cups

# Enable automatic security updates
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. File Permissions

```bash
# Restrict file permissions
chmod 700 /opt/smartapp  # Owner read/write/execute only
chmod 640 /etc/smartapp/.env  # Owner read/write, group read
chmod 755 /var/log/smartapp  # Readable by all, writable by owner
```

### 3. Resource Limits

```bash
# Edit /etc/security/limits.conf
smartapp soft nofile 65535
smartapp hard nofile 65535
smartapp soft nproc 4096
smartapp hard nproc 4096
smartapp soft memlock unlimited
smartapp hard memlock unlimited
```

### 4. Container Security (Docker)

```dockerfile
# Dockerfile security practices
FROM python:3.9-slim

# Create non-root user
RUN useradd -r -s /bin/bash smartapp

# Run as non-root
USER smartapp

# No setuid/setgid
RUN find / -perm /4000 -exec chmod a-s {} \; 2>/dev/null

# Scan image for vulnerabilities
# docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
#   aquasec/trivy image smartapp:latest
```

---

## Monitoring & Auditing

### 1. Audit Logging

```bash
# Enable auditd
sudo apt-get install auditd
sudo systemctl enable auditd
sudo systemctl start auditd

# Monitor file access
sudo auditctl -w /opt/smartapp/app.py -p wa -k app_changes
sudo auditctl -w /opt/smartapp/.env -p r -k env_access

# View audit logs
sudo ausearch -k app_changes
```

### 2. Security Scanning

```bash
# Scan Python dependencies
pip install safety
safety check

# Scan npm dependencies
npm audit

# Scan system for vulnerabilities
sudo apt-get install lynis
sudo lynis audit system

# Docker image scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image smartapp:latest
```

### 3. Intrusion Detection

```bash
# Install and configure AIDE
sudo apt-get install aide
sudo aideinit
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Run regular checks
sudo aide --check

# Schedule with cron
0 2 * * * /usr/bin/aide --check
```

### 4. Log Aggregation

```bash
# Centralize logs (ELK Stack, Splunk, etc.)
# All application logs sent to central server
# Retain logs for at least 90 days
# Implement log rotation and archival
```

---

## Incident Response

### 1. Security Incident Response Plan

- [ ] Define incident severity levels
- [ ] Create incident response team
- [ ] Document escalation procedures
- [ ] Establish communication protocols
- [ ] Define containment procedures
- [ ] Plan for evidence preservation
- [ ] Create recovery procedures
- [ ] Plan post-incident analysis

### 2. Data Breach Response

```
If a breach is suspected:

1. IMMEDIATE (First Hour)
   - Isolate affected systems
   - Preserve logs and evidence
   - Activate incident response team
   - Begin damage assessment

2. SHORT-TERM (First 24 Hours)
   - Contain the breach
   - Secure all systems
   - Notify management
   - Assess exposed data

3. MEDIUM-TERM (24-72 Hours)
   - Notify affected users
   - Notify relevant authorities
   - Implement fixes
   - Strengthen security

4. LONG-TERM (Ongoing)
   - Post-incident analysis
   - Implement improvements
   - Update security policies
   - Staff training
```

### 3. Security Update Process

```bash
# Regular security updates (at least monthly)
sudo apt-get update
sudo apt-get upgrade
sudo pip install --upgrade pip setuptools wheel
pip install --upgrade -r requirements.txt
npm update

# Test on staging first
# Deploy to production
# Verify no security issues
```

---

## Compliance & Standards

### 1. GDPR Compliance

- [ ] Implement data retention policies
- [ ] Provide data export functionality
- [ ] Implement right to be forgotten
- [ ] Obtain explicit consent for data processing
- [ ] Document data processing activities
- [ ] Perform data protection impact assessment

### 2. Security Standards

- [ ] Follow OWASP Top 10
- [ ] Follow NIST Cybersecurity Framework
- [ ] Implement CIS Controls
- [ ] Regular security training

### 3. Regular Audits

- [ ] Quarterly security audits
- [ ] Annual penetration testing
- [ ] Code security reviews
- [ ] Access control audits
- [ ] Compliance audits

---

## Security Checklist

- [ ] All secrets stored securely (not in code)
- [ ] All inputs validated and sanitized
- [ ] All outputs encoded properly
- [ ] Authentication implemented correctly
- [ ] Authorization checks on all endpoints
- [ ] HTTPS/TLS enabled for all traffic
- [ ] Security headers configured
- [ ] Logging and monitoring enabled
- [ ] Regular backups tested
- [ ] Incident response plan documented
- [ ] Security training completed
- [ ] Dependencies regularly updated
- [ ] Security scanning automated
- [ ] Firewall properly configured
- [ ] Database access restricted
- [ ] File permissions hardened
- [ ] SSH access hardened
- [ ] Error messages don't leak sensitive info
- [ ] Secrets not logged
- [ ] Rate limiting implemented

---

For more information, visit:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework/)
- [CIS Benchmarks](https://www.cisecurity.org/)
- [Flask Security Documentation](https://flask.palletsprojects.com/security/)
