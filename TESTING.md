# Testing Guide

This document provides comprehensive testing procedures for the Student-Professor Evaluation System.

## Table of Contents

1. [Manual Testing](#manual-testing)
2. [Database Testing](#database-testing)
3. [Security Testing](#security-testing)
4. [Performance Testing](#performance-testing)
5. [Multi-Language Testing](#multi-language-testing)

---

## Manual Testing

### Test 1: Complete Survey Flow

**Objective**: Verify end-to-end student survey experience

**Steps**:
1. Navigate to http://localhost:8000
2. Select a group with multiple professors assigned
3. For first professor:
   - Fill out all 19 rating questions
   - Add a comment in Q20
   - Click "Submit Evaluation"
4. For second professor:
   - Click "This is not my professor"
5. For remaining professors:
   - Complete or skip as desired
6. Verify "Thank You" page appears after last professor

**Expected Results**:
- ✓ Progress bar updates correctly
- ✓ Each professor displays on separate page
- ✓ Cannot proceed without answering required questions
- ✓ Skip button works without validation
- ✓ Thank you page shows after completion
- ✓ Group's `participated_students` count increments by 1

### Test 2: Admin Group Management

**Objective**: Test group CRUD operations

**Steps**:
1. Login to admin panel
2. Navigate to "Groups"
3. Create new group:
   - Group Name: "TEST-101"
   - Department: "Test Department"
   - Total Students: 25
4. Edit the group (change total students to 30)
5. Assign 2 professors to this group
6. Verify professors appear in inline section

**Expected Results**:
- ✓ Group created successfully
- ✓ Participation rate displays as 0%
- ✓ Professors can be assigned inline
- ✓ Group appears in student survey dropdown

### Test 3: Professor Analytics

**Objective**: Verify analytics display correctly

**Steps**:
1. Complete at least 3 surveys for a professor from different groups
2. Login to admin panel
3. Go to "Professors"
4. Click "View Analytics" for the test professor
5. Verify display shows:
   - All groups that evaluated this professor
   - Number of surveys per group
   - Average ratings per question
   - All comments

**Expected Results**:
- ✓ Data grouped by academic group
- ✓ Question averages calculated correctly (excluding N/A)
- ✓ Overall average displayed
- ✓ Comments listed
- ✓ Visual progress bars show rating scale
- ✓ Color coding: green (≤2), orange (≤3.5), red (>3.5)

### Test 4: Hidden Edit Section

**Objective**: Test manual survey editing capability

**Steps**:
1. Complete a survey as student
2. Navigate to http://localhost:8000/edit/
3. Login with admin credentials
4. Select professor from list
5. Find the survey just created
6. Click "Edit"
7. Change Q1 from 1 to 5
8. Change comment text
9. Save changes
10. Verify changes in admin analytics

**Expected Results**:
- ✓ Requires authentication
- ✓ All surveys for professor listed
- ✓ Can edit all 19 questions and comment
- ✓ Changes saved to database
- ✓ Updated averages reflect in analytics

### Test 5: Form Validation

**Objective**: Ensure proper validation on survey form

**Steps**:
1. Start a survey
2. Try to submit without answering all questions
3. Fill all questions except Q10
4. Try to submit
5. Fill Q10
6. Leave Q20 comment blank
7. Submit

**Expected Results**:
- ✓ Cannot submit with missing required fields
- ✓ Error messages display clearly
- ✓ Q20 comment is optional
- ✓ Scroll to first error on validation failure
- ✓ Form retains filled values after validation error

---

## Database Testing

### Test 1: Data Integrity

**Objective**: Verify database constraints and relationships

```python
# Run in Django shell: python manage.py shell

from evaluations.models import Group, Professor, GroupProfessor, Survey

# Test 1: Unique group names
group1 = Group.objects.create(group_name="CS-101", department="CS", total_students=30)
try:
    group2 = Group.objects.create(group_name="CS-101", department="Math", total_students=25)
    print("ERROR: Duplicate group name allowed")
except:
    print("✓ Unique constraint working")

# Test 2: Professor-Group assignment uniqueness
prof = Professor.objects.create(full_name="Dr. Test", department="CS")
gp1 = GroupProfessor.objects.create(group=group1, professor=prof)
try:
    gp2 = GroupProfessor.objects.create(group=group1, professor=prof)
    print("ERROR: Duplicate assignment allowed")
except:
    print("✓ Unique together constraint working")

# Test 3: Rating validation
survey = Survey(
    group=group1,
    professor=prof,
    q1=1, q2=2, q3=3, q4=4, q5=5,
    q6=6, q7=1, q8=2, q9=3, q10=4,
    q11=5, q12=6, q13=1, q14=2, q15=3,
    q16=4, q17=5, q18=6, q19=1
)
survey.full_clean()  # Should not raise error
survey.save()
print("✓ Valid ratings accepted")

# Test 4: Invalid rating
survey2 = Survey(
    group=group1,
    professor=prof,
    q1=7,  # Invalid!
    q2=2, q3=3, q4=4, q5=5, q6=6, q7=1, q8=2, q9=3, q10=4,
    q11=5, q12=6, q13=1, q14=2, q15=3, q16=4, q17=5, q18=6, q19=1
)
try:
    survey2.full_clean()
    print("ERROR: Invalid rating allowed")
except:
    print("✓ Rating validation working")
```

### Test 2: Cascade Deletion

**Objective**: Verify ON DELETE CASCADE behavior

```python
# In Django shell
from evaluations.models import Group, Professor, Survey

group = Group.objects.create(group_name="DELETE-TEST", department="Test", total_students=20)
prof = Professor.objects.create(full_name="Dr. Delete", department="Test")
GroupProfessor.objects.create(group=group, professor=prof)

# Create surveys
for i in range(5):
    Survey.objects.create(
        group=group, professor=prof,
        q1=1, q2=2, q3=3, q4=4, q5=5, q6=6, q7=1, q8=2, q9=3, q10=4,
        q11=5, q12=6, q13=1, q14=2, q15=3, q16=4, q17=5, q18=6, q19=1
    )

count_before = Survey.objects.filter(professor=prof).count()
print(f"Surveys before deletion: {count_before}")

# Delete professor
prof.delete()

count_after = Survey.objects.filter(professor=prof).count()
print(f"Surveys after deletion: {count_after}")
print("✓ Cascade deletion working" if count_after == 0 else "ERROR: Cascade failed")
```

### Test 3: Query Performance

**Objective**: Test query efficiency with large dataset

```python
# In Django shell
from evaluations.models import Group, Professor, Survey
from django.db import connection
from django.test.utils import override_settings

# Create test data
groups = [Group.objects.create(
    group_name=f"PERF-{i}",
    department="Test",
    total_students=30
) for i in range(10)]

profs = [Professor.objects.create(
    full_name=f"Prof {i}",
    department="Test"
) for i in range(20)]

# Assign professors to groups
for group in groups:
    for prof in profs[:5]:  # 5 profs per group
        GroupProfessor.objects.create(group=group, professor=prof)

# Create 1000 surveys
import random
for _ in range(1000):
    Survey.objects.create(
        group=random.choice(groups),
        professor=random.choice(profs),
        q1=random.randint(1,6), q2=random.randint(1,6),
        q3=random.randint(1,6), q4=random.randint(1,6),
        q5=random.randint(1,6), q6=random.randint(1,6),
        q7=random.randint(1,6), q8=random.randint(1,6),
        q9=random.randint(1,6), q10=random.randint(1,6),
        q11=random.randint(1,6), q12=random.randint(1,6),
        q13=random.randint(1,6), q14=random.randint(1,6),
        q15=random.randint(1,6), q16=random.randint(1,6),
        q17=random.randint(1,6), q18=random.randint(1,6),
        q19=random.randint(1,6)
    )

# Test query
from django.db import reset_queries
reset_queries()

surveys = Survey.objects.select_related('group', 'professor').all()
_ = list(surveys)

print(f"Number of queries: {len(connection.queries)}")
print("✓ Query optimization working" if len(connection.queries) < 5 else "WARNING: Too many queries")
```

---

## Security Testing

### Test 1: Anonymous Survey Submission

**Objective**: Verify no personal data is stored

**Steps**:
1. Complete a survey
2. Open Django shell:
   ```python
   from evaluations.models import Survey
   survey = Survey.objects.last()
   print(dir(survey))
   ```
3. Verify no fields like `student_id`, `ip_address`, `email`, etc.

**Expected Results**:
- ✓ Only group, professor, ratings, and timestamp stored
- ✓ No way to trace back to individual student

### Test 2: CSRF Protection

**Objective**: Ensure CSRF tokens required for form submission

**Steps**:
1. Open browser dev tools
2. Navigate to survey page
3. Try to submit form with invalid/missing CSRF token

**Expected Results**:
- ✓ 403 Forbidden error
- ✓ Form submission blocked

### Test 3: SQL Injection Prevention

**Objective**: Test for SQL injection vulnerabilities

**Steps**:
1. Try group selection with malicious input:
   ```
   ' OR '1'='1
   '; DROP TABLE evaluations_survey; --
   ```
2. Try search fields in admin with SQL keywords

**Expected Results**:
- ✓ Input sanitized by Django ORM
- ✓ No SQL errors
- ✓ No unauthorized data access

### Test 4: Authentication on Edit Section

**Objective**: Verify /edit/ requires login

**Steps**:
1. Open incognito/private browser window
2. Navigate to http://localhost:8000/edit/
3. Verify redirect to login page
4. Try accessing direct URLs:
   - /edit/professor/1/
   - /edit/survey/1/

**Expected Results**:
- ✓ Redirects to admin login
- ✓ Cannot access edit pages without authentication
- ✓ Session maintained after login

---

## Performance Testing

### Test 1: Page Load Times

**Objective**: Measure response times

**Method**: Use browser dev tools Network tab

**Benchmarks**:
- Home page: < 500ms
- Survey page: < 800ms
- Thank you page: < 300ms
- Admin pages: < 1s

### Test 2: Concurrent Users

**Objective**: Test system under load

**Tool**: Apache Bench or similar

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test home page (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/

# Test survey submission (requires valid session/CSRF - more complex)
```

**Expected Results**:
- ✓ No errors under normal load (10-20 concurrent users)
- ✓ Response time < 2s for 95% of requests

### Test 3: Database Query Optimization

**Objective**: Ensure efficient database queries

**Method**: Enable query debugging in settings

```python
# In settings.py (development only)
DEBUG = True
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

**Check**:
- Analytics page should use `select_related()` and `prefetch_related()`
- N+1 query problems avoided

---

## Multi-Language Testing

### Test 1: Language Switching

**Objective**: Verify all languages work correctly

**Steps**:
1. Navigate to home page
2. Switch to Uzbek (O'zbek) using dropdown
3. Verify UI elements translated
4. Switch to Russian (Русский)
5. Verify UI elements translated
6. Switch back to English

**Expected Results**:
- ✓ Language changes persist during session
- ✓ All UI elements translated
- ✓ Survey questions translated
- ✓ Error messages translated
- ✓ Admin panel respects language

### Test 2: Unicode Handling

**Objective**: Test non-Latin characters

**Steps**:
1. Create group with Cyrillic name: "Группа-101"
2. Create professor with Uzbek name: "O'qituvchi Ismi"
3. Complete survey in Russian
4. Add comment with mixed languages
5. View in admin analytics

**Expected Results**:
- ✓ All characters display correctly
- ✓ No encoding errors
- ✓ Database stores UTF-8 correctly
- ✓ Sorting works with non-Latin characters

---

## Mobile Responsive Testing

### Test Devices

Test on various screen sizes:
- **Mobile**: 375px (iPhone SE)
- **Mobile Large**: 414px (iPhone 12 Pro)
- **Tablet**: 768px (iPad)
- **Desktop**: 1024px+

### Test 1: Survey Form on Mobile

**Steps**:
1. Open survey on mobile device/emulator
2. Verify:
   - Rating buttons are touch-friendly
   - Text is readable
   - No horizontal scrolling
   - Buttons are easily clickable

### Test 2: Admin Panel on Mobile

**Steps**:
1. Access admin panel on mobile
2. Verify:
   - Tables are scrollable
   - Forms are usable
   - Analytics displays properly

---

## Automated Testing (Optional)

### Unit Tests

Create `evaluations/tests.py`:

```python
from django.test import TestCase, Client
from django.urls import reverse
from .models import Group, Professor, GroupProfessor, Survey

class SurveyFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = Group.objects.create(
            group_name="TEST-101",
            department="Test",
            total_students=30
        )
        self.prof = Professor.objects.create(
            full_name="Dr. Test",
            department="Test"
        )
        GroupProfessor.objects.create(
            group=self.group,
            professor=self.prof
        )
    
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_group_selection(self):
        response = self.client.post(reverse('home'), {
            'group': self.group.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_survey_submission(self):
        session = self.client.session
        session['survey_group_id'] = self.group.id
        session['survey_professor_index'] = 0
        session.save()
        
        response = self.client.post(reverse('survey'), {
            'q1': 1, 'q2': 2, 'q3': 3, 'q4': 4, 'q5': 5,
            'q6': 6, 'q7': 1, 'q8': 2, 'q9': 3, 'q10': 4,
            'q11': 5, 'q12': 6, 'q13': 1, 'q14': 2, 'q15': 3,
            'q16': 4, 'q17': 5, 'q18': 6, 'q19': 1,
            'q20_comment': 'Test comment'
        })
        
        self.assertTrue(Survey.objects.filter(
            group=self.group,
            professor=self.prof
        ).exists())
```

Run tests:
```bash
python manage.py test evaluations
```

---

## Test Checklist

### Pre-Deployment Testing

- [ ] All manual tests passed
- [ ] Database constraints verified
- [ ] Security tests passed
- [ ] Performance benchmarks met
- [ ] Multi-language support working
- [ ] Mobile responsive on all devices
- [ ] Admin panel fully functional
- [ ] Analytics display correctly
- [ ] Edit section secured and working
- [ ] Form validations working
- [ ] Error messages clear and helpful

### Production Testing (Post-Deployment)

- [ ] SSL certificate working
- [ ] All pages load over HTTPS
- [ ] Database backup/restore tested
- [ ] Monitoring alerts configured
- [ ] Log rotation working
- [ ] Error tracking active
- [ ] Performance under real load acceptable

---

## Bug Reporting Template

When reporting bugs, include:

```
**Description**: Clear description of the issue

**Steps to Reproduce**:
1. Step one
2. Step two
3. ...

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- Browser: Chrome 120
- Device: Desktop / Mobile
- OS: Windows 11
- Django version: 4.2
- Database: PostgreSQL 15

**Screenshots**: If applicable

**Error Messages**: Any error output from console/logs
```

---

## Continuous Testing

Recommend setting up:
1. **CI/CD Pipeline**: Run tests on every commit
2. **Scheduled Testing**: Weekly automated test runs
3. **Performance Monitoring**: Track response times in production
4. **User Acceptance Testing**: Real users test before major releases

---

**Remember**: Testing is ongoing! Add new tests as features are added.
