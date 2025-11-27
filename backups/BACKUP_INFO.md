# Backup and Restore Guide

## Created: November 22, 2025 - 18:14

## Current State Backup

**Database Backup:** `backups/survey_db_docker_20251122_181411.dump`

### What's Included:
- ✅ 10 Schools
- ✅ 17 Departments
- ✅ 30 Groups
- ✅ 65 Professors
- ✅ 206 Professor-Group Assignments
- ✅ 1 Admin User (yalgashev)

### Restore Instructions

#### Restore to Docker Database:

```powershell
# Copy backup into Docker container
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"
docker cp "d:\Python\survey\backups\survey_db_docker_20251122_181411.dump" survey_db:/tmp/restore.dump

# Restore the backup
docker compose exec db pg_restore -U postgres -d survey_db --clean --if-exists /tmp/restore.dump
```

#### Create New Backup:

```powershell
# Create backup in Docker
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"
docker compose exec db pg_dump -U postgres -d survey_db -F c -f /tmp/backup.dump

# Copy to local
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
docker cp survey_db:/tmp/backup.dump "d:\Python\survey\backups\survey_db_docker_$timestamp.dump"
```

## Admin Credentials

**Username:** yalgashev  
**Password:** admin123  
**URL:** http://localhost:8000/admin-panel/login/

## Docker Setup

All services running in Docker containers:
- PostgreSQL 16 (port 5432)
- Django Web App (port 8000)

### Start/Stop Commands:

```powershell
# Start
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"
docker compose up -d

# Stop
docker compose down

# View logs
docker compose logs -f

# Restart
docker compose restart
```

## Project Files Backup

All project files are in: `d:\Python\survey\`

Key files:
- `docker-compose.yml` - Docker orchestration
- `Dockerfile` - Django app container
- `config/settings.py` - Django settings
- `evaluations/` - Main application
- `templates/` - HTML templates
- `migrate_to_docker.py` - Data migration script

## Notes

- Database uses PostgreSQL 16 in Docker
- Old local database on port 5433 still exists but not used
- Data was migrated from local PostgreSQL 18 to Docker PostgreSQL 16
