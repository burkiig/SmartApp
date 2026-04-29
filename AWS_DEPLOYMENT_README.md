# AWS EC2 Ubuntu Deployment Guide for SmartApp

## 🚀 Quick Deployment Commands

After SSH into your AWS EC2 Ubuntu instance, run these commands:

```bash
# 1. Update system and install Docker
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 2. Clone repository
git clone https://github.com/yourusername/SmartApp.git
cd SmartApp/SmartApp

# 3. Create environment file
cp .env.example .env
nano .env  # Edit with your actual values

# 4. Build and start services
docker-compose build
docker-compose up -d

# 5. Check logs
docker-compose logs -f

# 6. Verify deployment
curl http://localhost/health
curl http://localhost/api/health
```

## 🔧 Environment Variables Setup

Edit `.env` file with your actual values:

```bash
# Database (IHS cPanel MySQL)
DB_HOST=your-ihs-cpanel-mysql-host.com
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_PORT=3306

# Security (Generate random keys)
SECRET_KEY=your-32-char-secret-key
JWT_SECRET_KEY=your-32-char-jwt-secret-key

# CORS (Add your domain)
CORS_ORIGINS=http://your-aws-ec2-public-ip,https://yourdomain.com
```

## 🌐 Domain & SSL Setup (Optional)

### 1. Point Domain to AWS EC2
- Go to your domain registrar
- Add A record pointing to your EC2 public IP

### 2. Install Nginx and Certbot
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 3. Configure SSL
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 4. Update Nginx Config
```bash
sudo nano /etc/nginx/sites-available/default
# Add your domain configuration
```

## 📊 Monitoring & Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check container status
docker-compose ps

# Restart services
docker-compose restart

# Update deployment
git pull origin main
docker-compose build
docker-compose up -d
```

## 🔍 Troubleshooting

### Backend not connecting to database
```bash
# Test MySQL connection from container
docker-compose exec backend bash
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "SELECT 1"
```

### Frontend not loading
```bash
# Check nginx configuration
docker-compose exec frontend nginx -t
```

### Port conflicts
```bash
# Check what's using ports
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000
```

## 🔒 Security Checklist

- [ ] Change default SSH port (22 → 2222)
- [ ] Configure AWS Security Groups (only allow 80, 443, 22)
- [ ] Set up SSH key authentication
- [ ] Install fail2ban
- [ ] Configure firewall (ufw)
- [ ] Regular security updates
- [ ] SSL certificate installation

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Test database connectivity
4. Check AWS Security Groups
5. Verify domain DNS settings