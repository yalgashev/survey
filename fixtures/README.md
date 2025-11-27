# Database Fixtures

This directory contains initial data for the survey system.

## Files

- `initial_data.json` - Contains all initial data including:
  - Schools (10 schools)
  - Departments (17 departments)
  - Groups (30 academic groups with semester information)
  - Professors (65 professors)
  - Group-Professor assignments (206 assignments)
  - Survey questions (19 questions in 3 languages: English, Uzbek, Russian)
  - Internship questions (in 3 languages)

## How to Use

### Loading Data into a Fresh Database

After running migrations, load the initial data:

```bash
# Using Docker
docker-compose exec web python manage.py loaddata fixtures/initial_data.json

# Without Docker
python manage.py loaddata fixtures/initial_data.json
```

### Complete Setup from Scratch

```bash
# 1. Run migrations to create database structure
docker-compose exec web python manage.py migrate

# 2. Load initial data
docker-compose exec web python manage.py loaddata fixtures/initial_data.json

# 3. Create superuser for admin access
docker-compose exec web python manage.py createsuperuser
```

## Updating Fixtures

If you need to update the fixture data after making changes:

```bash
docker-compose exec web python manage.py dumpdata \
  evaluations.School \
  evaluations.Department \
  evaluations.Group \
  evaluations.Professor \
  evaluations.GroupProfessor \
  evaluations.Question \
  evaluations.InternshipQuestion \
  --indent 2 \
  --output fixtures/initial_data.json
```

## Notes

- Survey responses (Survey, Answer, InternshipSurvey, InternshipAnswer) are NOT included in fixtures
- These are meant for initial setup only
- Production survey data should be backed up separately using database dumps
