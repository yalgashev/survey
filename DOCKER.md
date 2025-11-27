# Docker Deployment Guide

## Prerequisites
- Docker Desktop installed and running on Windows 11
- Docker Compose included with Docker Desktop

## Quick Start

### 1. Build and Run with Docker Compose

```powershell
# Build and start all services (PostgreSQL + Django)
docker-compose up --build
```

The application will be available at: **http://localhost:8000**

Admin panel: **http://localhost:8000/admin-panel/login/**

### 2. Stop Services

```powershell
# Stop services (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Initial Setup

### Create Superuser Account

After the containers are running, open a new terminal and run:

```powershell
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Load Sample Data (Optional)

```powershell
docker-compose exec web python setup_sample_data.py
```

## Docker Commands

### View Logs
```powershell
# All services
docker-compose logs -f

# Web service only
docker-compose logs -f web

# Database only
docker-compose logs -f db
```

### Run Django Commands
```powershell
# Make migrations
docker-compose exec web python manage.py makemigrations

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Django shell
docker-compose exec web python manage.py shell
```

### Database Access
```powershell
# Access PostgreSQL
docker-compose exec db psql -U postgres -d survey_db
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| web | 8000 | Django application |
| db | 5432 | PostgreSQL database |

## Environment Variables

The following environment variables can be customized in `docker-compose.yml`:

- `DB_NAME` - Database name (default: survey_db)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: 123456789)
- `DB_HOST` - Database host (default: db)
- `DB_PORT` - Database port (default: 5432)
- `DEBUG` - Debug mode (default: True)

## Troubleshooting

### Port Already in Use
If port 8000 or 5432 is already in use, modify the ports in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change host port to 8001
```

### Rebuild Containers
If you make changes to dependencies or Dockerfile:

```powershell
docker-compose up --build --force-recreate
```

### Reset Database
```powershell
docker-compose down -v
docker-compose up --build
```

## Production Deployment

For production, update:

1. Change `DEBUG=False` in settings
2. Use strong `SECRET_KEY`
3. Set proper `ALLOWED_HOSTS`
4. Use environment-specific passwords
5. Use Gunicorn/uWSGI instead of runserver
