# Deployment Guide - Production

This guide covers deploying the Student-Professor Evaluation System to a production environment.

## Deployment Options

### Option 1: Traditional Server (Linux)
### Option 2: Docker Container
### Option 3: Cloud Platform (AWS, Azure, Heroku)

---

## Option 1: Traditional Linux Server Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Root or sudo access
- Domain name (optional but recommended)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Supervisor (for process management)
sudo apt install supervisor -y
```

### Step 2: Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE survey_db;
CREATE USER survey_user WITH PASSWORD 'strong_password_here';
ALTER ROLE survey_user SET client_encoding TO 'utf8';
ALTER ROLE survey_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE survey_user SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE survey_db TO survey_user;
\q
```

### Step 3: Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/survey
sudo chown $USER:$USER /var/www/survey
cd /var/www/survey

# Copy your project files here
# Or clone from git: git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # WSGI server
```

### Step 4: Configure Django Settings

Create `config/production_settings.py`:

```python
from .settings import *
import os

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your.server.ip']

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'survey_db',
        'USER': 'survey_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = '/var/www/survey/staticfiles'
```

### Step 5: Environment Variables

Create `/var/www/survey/.env`:

```bash
SECRET_KEY=your-very-long-random-secret-key-here
DB_PASSWORD=your-database-password-here
DJANGO_SETTINGS_MODULE=config.production_settings
```

### Step 6: Prepare Django

```bash
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 7: Configure Gunicorn

Create `/var/www/survey/gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 120
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

Create log directory:
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown $USER:$USER /var/log/gunicorn
```

### Step 8: Configure Supervisor

Create `/etc/supervisor/conf.d/survey.conf`:

```ini
[program:survey]
command=/var/www/survey/venv/bin/gunicorn config.wsgi:application -c /var/www/survey/gunicorn_config.py
directory=/var/www/survey
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
environment=PATH="/var/www/survey/venv/bin",SECRET_KEY="your-secret",DB_PASSWORD="your-db-pass"
```

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start survey
```

### Step 9: Configure Nginx

Create `/etc/nginx/sites-available/survey`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/survey/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/survey /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 10: SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
```

---

## Option 2: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: survey_db
      POSTGRES_USER: survey_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - survey_network

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - static_volume:/app/staticfiles
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DEBUG=False
    depends_on:
      - db
    networks:
      - survey_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/app/staticfiles:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    networks:
      - survey_network

volumes:
  postgres_data:
  static_volume:

networks:
  survey_network:
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f
```

---

## Option 3: Cloud Platform Deployment

### Heroku Deployment

1. **Install Heroku CLI**

```bash
# Install CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login
```

2. **Create Heroku App**

```bash
heroku create survey-app-name
```

3. **Add PostgreSQL**

```bash
heroku addons:create heroku-postgresql:mini
```

4. **Configure Environment**

```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
```

5. **Create Procfile**

```
web: gunicorn config.wsgi --log-file -
release: python manage.py migrate
```

6. **Deploy**

```bash
git push heroku main
heroku run python manage.py createsuperuser
heroku open
```

---

## Post-Deployment Checklist

- [ ] Database backup configured
- [ ] SSL certificate installed and auto-renewal enabled
- [ ] Firewall configured (allow only 80, 443, SSH)
- [ ] Django DEBUG = False
- [ ] SECRET_KEY changed and secured
- [ ] Proper error monitoring set up
- [ ] Log rotation configured
- [ ] Regular security updates scheduled
- [ ] Admin panel accessible only via secure connection
- [ ] Database credentials secured
- [ ] Application performance monitored

## Monitoring & Maintenance

### Log Management

```bash
# View application logs
sudo supervisorctl tail -f survey

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View Gunicorn logs
sudo tail -f /var/log/gunicorn/access.log
```

### Database Backup Script

Create `/var/www/survey/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/survey"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U survey_user survey_db > $BACKUP_DIR/survey_db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /var/www/survey/backup.sh
```

### Performance Monitoring

Consider adding:
- **Sentry** for error tracking
- **New Relic** for application performance
- **Prometheus + Grafana** for metrics

## Security Best Practices

1. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Firewall Configuration**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **Fail2Ban** (protect against brute force)
   ```bash
   sudo apt install fail2ban -y
   sudo systemctl enable fail2ban
   ```

4. **Database Security**
   - Use strong passwords
   - Limit database connections to localhost
   - Regular backups

## Scaling Considerations

### For High Traffic

1. **Database Optimization**
   - Add read replicas
   - Enable connection pooling (PgBouncer)
   - Optimize queries with indexes

2. **Caching Layer**
   - Add Redis for session storage
   - Cache query results
   - Use CDN for static files

3. **Load Balancing**
   - Multiple application servers
   - Nginx load balancer
   - Session storage in Redis/database

4. **Monitoring**
   - Set up alerts for high CPU/memory
   - Monitor response times
   - Track error rates

## Support & Troubleshooting

Common production issues and solutions in the main README.md file.

---

**Important**: Always test deployment process in a staging environment before deploying to production!
