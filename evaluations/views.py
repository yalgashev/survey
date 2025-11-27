from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _, get_language
from django.db import transaction
from .models import Group, Professor, GroupProfessor, Survey, Question, Answer, InternshipQuestion, InternshipSurvey, InternshipAnswer
from .forms import GroupSelectionForm, DynamicSurveyForm, DynamicInternshipSurveyForm


def home(request):
    """Landing page with group selection"""
    if request.method == 'POST':
        form = GroupSelectionForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            language = form.cleaned_data['language']
            # Store group_id and language in session
            request.session['survey_group_id'] = group.id
            request.session['survey_language'] = language
            request.session['survey_professor_index'] = 0
            return redirect('survey')
    else:
        form = GroupSelectionForm()
    
    return render(request, 'evaluations/home.html', {'form': form})


def survey(request):
    """Sequential professor evaluation with dynamic questions"""
    # Get group from session
    group_id = request.session.get('survey_group_id')
    if not group_id:
        return redirect('home')
    
    group = get_object_or_404(Group, id=group_id)
    
    # Get list of professors for this group
    professor_assignments = GroupProfessor.objects.filter(group=group).select_related('professor')
    professors = [assignment.professor for assignment in professor_assignments]
    
    if not professors:
        messages.warning(request, _('No professors assigned to this group.'))
        return redirect('home')
    
    # Get current professor index
    current_index = request.session.get('survey_professor_index', 0)
    
    # Check if we've finished all professors
    if current_index >= len(professors):
        return redirect('thank_you')
    
    current_professor = professors[current_index]
    
    # Get language from session (set during group selection)
    current_language = request.session.get('survey_language', 'en')
    
    # Get all active questions with localized text
    questions_qs = Question.objects.filter(is_active=True).order_by('order')
    questions = []
    for q in questions_qs:
        questions.append({
            'id': q.id,
            'question_type': q.question_type,
            'order': q.order,
            'get_text': q.get_text(current_language)
        })
    
    # Handle form submission
    if request.method == 'POST':
        # Check if user clicked "Not my professor"
        if 'skip_professor' in request.POST:
            # Skip this professor, move to next
            request.session['survey_professor_index'] = current_index + 1
            return redirect('survey')
        
        # Otherwise, process the evaluation form
        form = DynamicSurveyForm(request.POST, language=current_language)
        if form.is_valid():
            # Create survey session
            survey = Survey.objects.create(
                group=group,
                professor=current_professor
            )
            
            # Save all answers
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = int(field_name.split('_')[1])
                    question = Question.objects.get(id=question_id)
                    
                    if question.question_type == 'rating':
                        Answer.objects.create(
                            survey=survey,
                            question=question,
                            rating_value=int(value)
                        )
                    else:
                        Answer.objects.create(
                            survey=survey,
                            question=question,
                            text_value=value
                        )
            
            # Move to next professor
            request.session['survey_professor_index'] = current_index + 1
            
            # Check if this was the last professor
            if current_index + 1 >= len(professors):
                # Check if group needs to complete internship survey (semester 2-8)
                if group.semester > 1:
                    # Keep group_id in session for internship survey
                    request.session.pop('survey_professor_index', None)
                    return redirect('internship_survey')
                else:
                    # Semester 1 - go directly to thank you
                    # Increment participated students count
                    with transaction.atomic():
                        group.participated_students += 1
                        group.save()
                    
                    # Clear session data
                    request.session.pop('survey_group_id', None)
                    request.session.pop('survey_professor_index', None)
                    
                    return redirect('thank_you')
            
            return redirect('survey')
    else:
        form = DynamicSurveyForm(language=current_language)
    
    # Calculate progress
    total_professors = len(professors)
    progress_percentage = ((current_index + 1) / total_professors) * 100
    
    context = {
        'form': form,
        'professor': current_professor,
        'group': group,
        'current_number': current_index + 1,
        'total_professors': total_professors,
        'progress_percentage': progress_percentage,
        'questions': questions,
    }
    
    return render(request, 'evaluations/survey.html', context)


def thank_you(request):
    """Thank you page after completing survey"""
    # Clear any remaining session data
    request.session.pop('survey_group_id', None)
    request.session.pop('survey_professor_index', None)
    request.session.pop('survey_language', None)
    
    return render(request, 'evaluations/thank_you.html')


@login_required
def edit_professor_list(request):
    """Hidden admin section - list professors for editing surveys"""
    professors = Professor.objects.all().order_by('full_name')
    return render(request, 'evaluations/edit_professor_list.html', {'professors': professors})


@login_required
def edit_professor_surveys(request, professor_id):
    """Hidden admin section - list all surveys for a professor"""
    professor = get_object_or_404(Professor, id=professor_id)
    surveys = Survey.objects.filter(professor=professor).select_related('group').order_by('-created_at')
    
    return render(request, 'evaluations/edit_professor_surveys.html', {
        'professor': professor,
        'surveys': surveys
    })


@login_required
def edit_survey(request, survey_id):
    """Hidden admin section - edit a specific survey"""
    survey = get_object_or_404(Survey, id=survey_id)
    
    if request.method == 'POST':
        form = SurveyEditForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            messages.success(request, _('Survey updated successfully.'))
            return redirect('edit_professor_surveys', professor_id=survey.professor.id)
    else:
        form = SurveyEditForm(instance=survey)
    
    context = {
        'form': form,
        'survey': survey,
    }
    
    return render(request, 'evaluations/edit_survey.html', context)


def internship_survey(request):
    """Internship evaluation survey (for semester 2-8 students only)"""
    # Get group from session
    group_id = request.session.get('survey_group_id')
    if not group_id:
        return redirect('home')
    
    group = get_object_or_404(Group, id=group_id)
    
    # Security check: Only semester 2-8 students should see this
    if group.semester <= 1:
        messages.warning(request, _('Internship survey is not available for first semester students.'))
        return redirect('thank_you')
    
    # Get language from session (set during group selection)
    current_language = request.session.get('survey_language', 'en')
    
    # Get all active internship questions with localized text
    questions_qs = InternshipQuestion.objects.filter(is_active=True).order_by('order')
    questions = []
    for q in questions_qs:
        questions.append({
            'id': q.id,
            'question_type': q.question_type,
            'order': q.order,
            'get_text': q.get_text(current_language)
        })
    
    # Handle form submission
    if request.method == 'POST':
        form = DynamicInternshipSurveyForm(request.POST, language=current_language)
        if form.is_valid():
            # Create internship survey session
            internship_survey = InternshipSurvey.objects.create(
                group=group
            )
            
            # Save all answers
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = int(field_name.split('_')[1])
                    question = InternshipQuestion.objects.get(id=question_id)
                    
                    if question.question_type == 'rating':
                        InternshipAnswer.objects.create(
                            internship_survey=internship_survey,
                            question=question,
                            rating_value=int(value)
                        )
                    else:
                        InternshipAnswer.objects.create(
                            internship_survey=internship_survey,
                            question=question,
                            text_value=value
                        )
            
            # Now increment participated students count
            with transaction.atomic():
                group.participated_students += 1
                group.save()
            
            # Clear session data
            request.session.pop('survey_group_id', None)
            
            return redirect('thank_you')
    else:
        form = DynamicInternshipSurveyForm(language=current_language)
    
    context = {
        'form': form,
        'group': group,
        'questions': questions,
    }
    
    return render(request, 'evaluations/internship_survey.html', context)
