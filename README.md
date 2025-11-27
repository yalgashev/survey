# Student-Professor Evaluation System

A comprehensive, mobile-friendly web application for anonymous student evaluations of professors.

## Features

- ✅ Anonymous student surveys (no personal data stored)
- ✅ Multi-language support (English, Uzbek, Russian)
- ✅ Sequential professor evaluation flow
- ✅ Skip option for professors not in student's classes
- ✅ Responsive mobile-first design
- ✅ Comprehensive admin analytics
- ✅ Hidden admin edit section for manual survey adjustments
- ✅ Progress tracking for students
- ✅ Detailed reporting per professor and group

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Django 4.2+

## Installation

### 1. Clone or Extract Project

Extract the project to your desired location.

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Database

Edit `config/settings.py` and update the database settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'survey_db',
        'USER': 'your_postgres_user',
        'PASSWORD': 'your_postgres_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Create the PostgreSQL database:

```sql
CREATE DATABASE survey_db;
```

### 5. Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```powershell
python manage.py createsuperuser
```

### 7. Compile Translation Messages

```powershell
python manage.py compilemessages
```

If this fails, you can skip it for now (translations will use English defaults).

### 8. Run Development Server

```powershell
python manage.py runserver
```

Visit: `http://localhost:8000`

## Usage

### Student Flow

1. Go to `http://localhost:8000`
2. Select language (optional)
3. Select your academic group
4. Evaluate each professor sequentially:
   - Answer all 19 rating questions
   - Optionally provide comments (Question 20)
   - Click "Submit Evaluation" OR "This is not my professor"
5. Receive thank you message after completing all evaluations

### Admin Access

1. Go to `http://localhost:8000/admin`
2. Login with superuser credentials
3. Manage:
   - **Groups**: Create academic groups/classes
   - **Professors**: Add professors
   - **Group-Professor Assignments**: Assign professors to groups
   - **Survey Responses**: View all submitted surveys
   - **Analytics**: Click "View Analytics" next to any professor

### Hidden Edit Section

Accessible at: `http://localhost:8000/edit/`

**Requires authentication** - Login with admin credentials.

Allows manual editing of survey responses:
1. Select a professor
2. View all survey responses
3. Click "Edit" to modify ratings or comments
4. Save changes

## Database Schema

### Group
- group_name (unique)
- department
- total_students
- participated_students

### Professor
- full_name
- department

### GroupProfessor (Assignment)
- group (FK)
- professor (FK)

### Survey (Evaluation Response)
- group (FK)
- professor (FK)
- q1 through q19 (integer 1-6)
- q20_comment (text, optional)
- created_at (timestamp)

## Rating Scale

1 = Strongly Agree (best)  
2 = Agree  
3 = Neither Agree nor Disagree  
4 = Disagree  
5 = Strongly Disagree (worst)  
6 = Not Applicable  

**Note**: Lower numbers = better ratings; higher numbers = worse ratings

## Multi-Language Support

Supported languages:
- English (en) - Default
- Uzbek (uz)
- Russian (ru)

Language can be changed using the dropdown in the top-right corner.

To add/edit translations:

1. Edit translation files in `locale/` directory
2. Run: `python manage.py compilemessages`

## Security Notes

- Change `SECRET_KEY` in `config/settings.py` for production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` properly
- Use environment variables for sensitive data
- Enable HTTPS in production
- Protect `/edit/` route with proper authentication

## Technical Constraints

- **No logging module used** - As per project requirements
- All surveys are completely anonymous
- No IP addresses or student identifiers stored

## Project Structure

```
survey1/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── evaluations/         # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── forms.py         # Form definitions
│   ├── admin.py         # Admin configuration
│   ├── urls.py          # URL routing
│   └── templatetags/    # Custom template filters
├── templates/           # HTML templates
│   ├── base.html
│   ├── evaluations/     # Survey templates
│   └── admin/           # Admin templates
├── locale/              # Translation files
├── manage.py
└── requirements.txt
```

## Support & Maintenance

For issues or questions:
1. Check database connection settings
2. Ensure PostgreSQL is running
3. Verify all migrations are applied
4. Check Django version compatibility

## License

Educational/Internal Use
