# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] PostgreSQL 12 or higher installed and running
- [ ] Git (optional, for version control)

## Quick Setup (5 minutes)

### Step 1: Database Setup

Open PostgreSQL and create the database:

```sql
CREATE DATABASE survey_db;
```

### Step 2: Configure Database Connection

Edit `config/settings.py` (lines 51-59):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'survey_db',
        'USER': 'your_postgres_username',      # Change this
        'PASSWORD': 'your_postgres_password',  # Change this
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 3: Run Setup Script

Open PowerShell in the project directory and run:

```powershell
.\setup.ps1
```

This script will:
- Create virtual environment
- Install dependencies
- Run database migrations
- Create superuser account
- Optionally load sample data

### Step 4: Start Server

```powershell
python manage.py runserver
```

### Step 5: Access Application

- **Student Survey**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Edit Section**: http://localhost:8000/edit/ (requires login)

## Manual Setup (Alternative)

If the automated script doesn't work, follow these steps:

### 1. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Update Database Settings

Edit `config/settings.py` with your PostgreSQL credentials.

### 4. Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User

```powershell
python manage.py createsuperuser
```

Follow prompts to create username and password.

### 6. Load Sample Data (Optional)

```powershell
python setup_sample_data.py
```

### 7. Run Server

```powershell
python manage.py runserver
```

## First Steps After Installation

### 1. Login to Admin Panel

Visit http://localhost:8000/admin and login with superuser credentials.

### 2. Create Academic Data

**Add Groups:**
1. Click "Groups" → "Add Group"
2. Enter: Group Name, Department, Total Students
3. Save

**Add Professors:**
1. Click "Professors" → "Add Professor"
2. Enter: Full Name, Department
3. Save

**Assign Professors to Groups:**
1. Click "Groups" → Select a group
2. Scroll to "Group-Professor Assignments" section
3. Add professors that teach this group
4. Save

OR

1. Click "Group-Professor Assignments" → "Add Assignment"
2. Select Group and Professor
3. Save

### 3. Test Student Survey

1. Go to http://localhost:8000
2. Select a group (with assigned professors)
3. Fill out evaluation for each professor
4. Test "This is not my professor" button
5. Complete all professors to see thank you page

### 4. View Analytics

1. Login to admin panel
2. Go to "Professors"
3. Click "View Analytics" next to any professor
4. See detailed ratings and comments per group

### 5. Test Edit Section

1. Go to http://localhost:8000/edit/
2. Login if prompted
3. Select a professor
4. Edit any survey response
5. Save changes

## Troubleshooting

### Database Connection Error

**Problem**: `django.db.utils.OperationalError: could not connect to server`

**Solution**:
1. Ensure PostgreSQL is running
2. Check database credentials in `config/settings.py`
3. Verify database `survey_db` exists

### Migration Errors

**Problem**: Migrations fail to apply

**Solution**:
```powershell
python manage.py makemigrations evaluations
python manage.py migrate --run-syncdb
```

### Static Files Not Loading

**Problem**: CSS/Bootstrap not appearing

**Solution**:
```powershell
python manage.py collectstatic
```

In production, configure web server to serve static files.

### Virtual Environment Not Activating

**Problem**: PowerShell execution policy error

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### No Module Named 'evaluations'

**Problem**: Import errors

**Solution**:
1. Ensure you're in the project root directory
2. Activate virtual environment
3. Reinstall dependencies:
```powershell
pip install -r requirements.txt
```

## Language Support

The system supports three languages:
- **English** (default)
- **Uzbek** (O'zbek)
- **Russian** (Русский)

To switch language:
1. Use dropdown in top-right corner of any page
2. Language preference is saved in session

## Data Management

### Backing Up Database

```powershell
pg_dump -U postgres survey_db > backup.sql
```

### Restoring Database

```powershell
psql -U postgres survey_db < backup.sql
```

### Exporting Survey Data

Use Django admin panel:
1. Go to "Survey Responses"
2. Select surveys to export
3. Use admin actions or Django shell:

```python
python manage.py shell
from evaluations.models import Survey
import csv

surveys = Survey.objects.all()
# Export to CSV logic here
```

## Security Checklist for Production

- [ ] Change `SECRET_KEY` in settings.py
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS
- [ ] Set up proper PostgreSQL user permissions
- [ ] Implement rate limiting for survey submissions
- [ ] Add CSRF protection (already enabled)
- [ ] Configure proper backup strategy
- [ ] Set up application monitoring

## Performance Tips

### For Large Scale Deployments

1. **Database Indexing**: Already configured in models
2. **Caching**: Add Redis for session management
3. **Static Files**: Use CDN or separate static server
4. **Database Connection Pooling**: Use pgBouncer
5. **Load Balancing**: Deploy multiple Django instances

## Support

For technical issues:
1. Check database connection
2. Verify PostgreSQL is running
3. Ensure migrations are applied
4. Check Django and Python versions
5. Review error messages in terminal

## Next Steps

1. Customize survey questions (edit `evaluations/models.py` and forms)
2. Add your institution's branding (edit templates)
3. Configure email notifications (optional)
4. Set up automated backups
5. Deploy to production server

Enjoy using the Student-Professor Evaluation System! 🎓
