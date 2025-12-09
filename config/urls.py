"""
URL configuration for survey project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from evaluations import admin_views

# Custom admin URLs (non-i18n)
admin_patterns = [
    path('login/', admin_views.admin_login_view, name='admin_login'),
    path('logout/', admin_views.admin_logout_view, name='admin_logout'),
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Schools
    path('schools/', admin_views.schools_list, name='admin_schools_list'),
    path('schools/add/', admin_views.school_add, name='admin_school_add'),
    path('schools/<int:pk>/edit/', admin_views.school_edit, name='admin_school_edit'),
    path('schools/<int:pk>/delete/', admin_views.school_delete, name='admin_school_delete'),
    
    # Departments
    path('departments/', admin_views.departments_list, name='admin_departments_list'),
    path('departments/add/', admin_views.department_add, name='admin_department_add'),
    path('departments/<int:pk>/edit/', admin_views.department_edit, name='admin_department_edit'),
    path('departments/<int:pk>/delete/', admin_views.department_delete, name='admin_department_delete'),
    
    # Groups
    path('groups/', admin_views.groups_list, name='admin_groups_list'),
    path('groups/add/', admin_views.group_add, name='admin_group_add'),
    path('groups/<int:pk>/edit/', admin_views.group_edit, name='admin_group_edit'),
    path('groups/<int:pk>/delete/', admin_views.group_delete, name='admin_group_delete'),
    path('group-participation/', admin_views.group_participation, name='admin_group_participation'),
    
    # Professors
    path('professors/', admin_views.professors_list, name='admin_professors_list'),
    path('professors/add/', admin_views.professor_add, name='admin_professor_add'),
    path('professors/<int:pk>/edit/', admin_views.professor_edit, name='admin_professor_edit'),
    path('professors/<int:pk>/delete/', admin_views.professor_delete, name='admin_professor_delete'),
    path('professors/<int:pk>/analytics/', admin_views.professor_analytics, name='admin_professor_analytics'),
    path('professors-rating/', admin_views.admin_professors_rating, name='admin_professors_rating'),
    path('professors-rating/export/', admin_views.admin_professors_rating_export, name='admin_professors_rating_export'),
    
    # Surveys
    path('surveys/', admin_views.surveys_list, name='admin_surveys_list'),
    path('surveys/<int:pk>/', admin_views.survey_detail, name='admin_survey_detail'),
    path('surveys/<int:pk>/delete/', admin_views.survey_delete, name='admin_survey_delete'),
    
    # Assignments
    path('assignments/', admin_views.assignments_list, name='admin_assignments_list'),
    path('assignments/add/', admin_views.assignment_add, name='admin_assignment_add'),
    path('assignments/<int:pk>/delete/', admin_views.assignment_delete, name='admin_assignment_delete'),
    
    # Questions
    path('questions/', admin_views.questions_list, name='admin_questions_list'),
    path('questions/add/', admin_views.question_add, name='admin_question_add'),
    path('questions/<int:pk>/edit/', admin_views.question_edit, name='admin_question_edit'),
    path('questions/<int:pk>/delete/', admin_views.question_delete, name='admin_question_delete'),
    
    # Internship Questions
    path('internship-questions/', admin_views.internship_questions_list, name='admin_internship_questions_list'),
    path('internship-questions/add/', admin_views.internship_question_add, name='admin_internship_question_add'),
    path('internship-questions/<int:pk>/edit/', admin_views.internship_question_edit, name='admin_internship_question_edit'),
    path('internship-questions/<int:pk>/delete/', admin_views.internship_question_delete, name='admin_internship_question_delete'),
    
    # Internship Surveys
    path('internship-surveys/', admin_views.internship_surveys_list, name='admin_internship_surveys_list'),
    path('internship-surveys/<int:pk>/', admin_views.internship_survey_detail, name='admin_internship_survey_detail'),
    path('internship-surveys/<int:pk>/delete/', admin_views.internship_survey_delete, name='admin_internship_survey_delete'),
    
    # Internship Department Rating
    path('internship-department-rating/', admin_views.admin_internship_department_rating, name='admin_internship_department_rating'),
    path('internship-department-rating/export/', admin_views.admin_internship_department_rating_export, name='admin_internship_department_rating_export'),
    
    # Internship School Rating
    path('internship-school-rating/', admin_views.admin_internship_school_rating, name='admin_internship_school_rating'),
    path('internship-school-rating/export/', admin_views.admin_internship_school_rating_export, name='admin_internship_school_rating_export'),
]

urlpatterns = [
    path('admin-panel/', include(admin_patterns)),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Add i18n patterns for multi-language support
urlpatterns += i18n_patterns(
    path('', include('evaluations.urls')),
)
