from django.urls import path
from . import views

urlpatterns = [
    # Public survey flow
    path('', views.home, name='home'),
    path('survey/', views.survey, name='survey'),
    path('internship-survey/', views.internship_survey, name='internship_survey'),
    path('thank-you/', views.thank_you, name='thank_you'),
    
    # Hidden admin edit section (requires authentication)
    path('edit/', views.edit_professor_list, name='edit_professor_list'),
    path('edit/professor/<int:professor_id>/', views.edit_professor_surveys, name='edit_professor_surveys'),
    path('edit/survey/<int:survey_id>/', views.edit_survey, name='edit_survey'),
]
