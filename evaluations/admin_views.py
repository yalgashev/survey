from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import School, Department, Group, Professor, GroupProfessor, Survey, Question, Answer, InternshipQuestion, InternshipSurvey, InternshipAnswer


def is_admin(user):
    """Check if user is staff/admin"""
    return user.is_staff or user.is_superuser


def admin_login_view(request):
    """Custom admin login page"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and is_admin(user):
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'admin_custom/login.html')


@login_required
@user_passes_test(is_admin)
def admin_logout_view(request):
    """Admin logout"""
    logout(request)
    return redirect('admin_login')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard"""
    # Statistics
    total_groups = Group.objects.count()
    total_professors = Professor.objects.count()
    total_surveys = Survey.objects.count()
    
    # Calculate total participation
    groups = Group.objects.all()
    total_students = sum(g.total_students for g in groups)
    total_participated = sum(g.participated_students for g in groups)
    
    # Recent surveys (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_surveys = Survey.objects.filter(created_at__gte=week_ago).count()
    
    # Top rated professors
    top_professors = []
    for prof in Professor.objects.all():
        surveys = prof.surveys.all()
        if surveys.exists():
            total_avg = 0
            count = 0
            for survey in surveys:
                avg = survey.get_average_rating()
                if avg > 0:
                    total_avg += avg
                    count += 1
            if count > 0:
                avg_rating = total_avg / count
                top_professors.append({
                    'id': prof.id,
                    'name': prof.full_name,
                    'school': prof.school,
                    'rating': round(avg_rating, 2),
                    'count': surveys.count()
                })
    
    top_professors.sort(key=lambda x: x['rating'])
    top_professors = top_professors[:5]
    
    # Recent activity
    recent_activity = Survey.objects.select_related('group', 'professor').order_by('-created_at')[:10]
    
    # Groups with participation
    groups_data = []
    for group in Group.objects.all()[:5]:
        rate = 0
        if group.total_students > 0:
            rate = (group.participated_students / group.total_students) * 100
        groups_data.append({
            'id': group.id,
            'name': group.group_name,
            'department': group.department,
            'participated': group.participated_students,
            'total': group.total_students,
            'rate': round(rate, 1)
        })
    
    context = {
        'total_groups': total_groups,
        'total_professors': total_professors,
        'total_surveys': total_surveys,
        'total_students': total_students,
        'total_participated': total_participated,
        'recent_surveys': recent_surveys,
        'top_professors': top_professors,
        'recent_activity': recent_activity,
        'groups_data': groups_data,
    }
    
    return render(request, 'admin_custom/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def groups_list(request):
    """List all groups"""
    groups = Group.objects.all().order_by('group_name')
    return render(request, 'admin_custom/groups_list.html', {'groups': groups})


@login_required
@user_passes_test(is_admin)
def group_add(request):
    """Add new group"""
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        department_id = request.POST.get('department')
        semester = request.POST.get('semester', 1)
        total_students = request.POST.get('total_students', 0)
        
        department = get_object_or_404(Department, pk=department_id)
        
        Group.objects.create(
            group_name=group_name,
            department=department,
            semester=int(semester),
            total_students=int(total_students),
            participated_students=0
        )
        messages.success(request, 'Group added successfully!')
        return redirect('admin_groups_list')
    
    departments = Department.objects.all()
    return render(request, 'admin_custom/group_form.html', {'action': 'Add', 'departments': departments})


@login_required
@user_passes_test(is_admin)
def group_edit(request, pk):
    """Edit group"""
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        group.group_name = request.POST.get('group_name')
        department_id = request.POST.get('department')
        group.department = get_object_or_404(Department, pk=department_id)
        group.semester = int(request.POST.get('semester', 1))
        group.total_students = int(request.POST.get('total_students', 0))
        group.save()
        messages.success(request, 'Group updated successfully!')
        return redirect('admin_groups_list')
    
    departments = Department.objects.all()
    return render(request, 'admin_custom/group_form.html', {'group': group, 'action': 'Edit', 'departments': departments})


@login_required
@user_passes_test(is_admin)
def group_delete(request, pk):
    """Delete group"""
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted successfully!')
        return redirect('admin_groups_list')
    return render(request, 'admin_custom/group_confirm_delete.html', {'group': group})


@login_required
@user_passes_test(is_admin)
def group_participation(request):
    """View group participation statistics"""
    groups = Group.objects.all().order_by('group_name')
    
    # Calculate statistics for each group
    group_stats = []
    for group in groups:
        if group.total_students > 0:
            participation_rate = (group.participated_students / group.total_students) * 100
        else:
            participation_rate = 0
        
        group_stats.append({
            'group': group,
            'participated': group.participated_students,
            'total': group.total_students,
            'rate': participation_rate
        })
    
    # Overall statistics
    total_students = sum(g.total_students for g in groups)
    total_participated = sum(g.participated_students for g in groups)
    overall_rate = (total_participated / total_students * 100) if total_students > 0 else 0
    
    context = {
        'group_stats': group_stats,
        'total_students': total_students,
        'total_participated': total_participated,
        'overall_rate': overall_rate
    }
    
    return render(request, 'admin_custom/group_participation.html', context)


@login_required
@user_passes_test(is_admin)
def professors_list(request):
    """List all professors"""
    professors = Professor.objects.all().order_by('full_name')
    return render(request, 'admin_custom/professors_list.html', {'professors': professors})


@login_required
@user_passes_test(is_admin)
def professor_add(request):
    """Add new professor"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        school_id = request.POST.get('school')
        email = request.POST.get('email', '')
        
        school = get_object_or_404(School, pk=school_id)
        
        Professor.objects.create(
            full_name=full_name,
            school=school,
            email=email
        )
        messages.success(request, 'Professor added successfully!')
        return redirect('admin_professors_list')
    
    schools = School.objects.all().order_by('name')
    return render(request, 'admin_custom/professor_form.html', {'action': 'Add', 'schools': schools})


@login_required
@user_passes_test(is_admin)
def professor_edit(request, pk):
    """Edit professor"""
    professor = get_object_or_404(Professor, pk=pk)
    
    if request.method == 'POST':
        professor.full_name = request.POST.get('full_name')
        school_id = request.POST.get('school')
        professor.school = get_object_or_404(School, pk=school_id)
        professor.email = request.POST.get('email', '')
        professor.save()
        messages.success(request, 'Professor updated successfully!')
        return redirect('admin_professors_list')
    
    schools = School.objects.all().order_by('name')
    return render(request, 'admin_custom/professor_form.html', {'professor': professor, 'action': 'Edit', 'schools': schools})


@login_required
@user_passes_test(is_admin)
def professor_delete(request, pk):
    """Delete professor"""
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == 'POST':
        professor.delete()
        messages.success(request, 'Professor deleted successfully!')
        return redirect('admin_professors_list')
    return render(request, 'admin_custom/professor_confirm_delete.html', {'professor': professor})


@login_required
@user_passes_test(is_admin)
def professor_analytics(request, pk):
    """Professor analytics page"""
    professor = get_object_or_404(Professor, pk=pk)
    surveys = professor.surveys.select_related('group').all()
    
    # Group data by group
    groups_data = {}
    for survey in surveys:
        group_name = survey.group.group_name
        if group_name not in groups_data:
            groups_data[group_name] = {
                'group': survey.group,
                'surveys': [],
                'question_totals': {f'q{i}': [] for i in range(1, 20)},
            }
        
        groups_data[group_name]['surveys'].append(survey)
        
        # Collect question ratings
        for i in range(1, 20):
            q_field = f'q{i}'
            value = getattr(survey, q_field)
            if value and value != 6:  # Exclude N/A
                groups_data[group_name]['question_totals'][q_field].append(value)
    
    # Calculate averages
    for group_name, data in groups_data.items():
        data['survey_count'] = len(data['surveys'])
        data['question_averages'] = {}
        total_avg_sum = 0
        total_avg_count = 0
        
        for q_field, values in data['question_totals'].items():
            if values:
                avg = sum(values) / len(values)
                data['question_averages'][q_field] = round(avg, 2)
                total_avg_sum += avg
                total_avg_count += 1
            else:
                data['question_averages'][q_field] = None
        
        if total_avg_count > 0:
            data['overall_average'] = round(total_avg_sum / total_avg_count, 2)
        else:
            data['overall_average'] = None
        
        # Get comments
        data['comments'] = [s.q20_comment for s in data['surveys'] if s.q20_comment]
    
    context = {
        'professor': professor,
        'groups_data': groups_data,
    }
    
    return render(request, 'admin_custom/professor_analytics.html', context)


@login_required
@user_passes_test(is_admin)
def surveys_list(request):
    """List all surveys"""
    surveys = Survey.objects.select_related('group', 'professor').order_by('-created_at')
    return render(request, 'admin_custom/surveys_list.html', {'surveys': surveys})


@login_required
@user_passes_test(is_admin)
def survey_detail(request, pk):
    """View survey detail"""
    survey = get_object_or_404(Survey, pk=pk)
    
    # Get all answers for this survey
    answers = Answer.objects.filter(survey=survey).select_related('question').order_by('question__order')
    
    # Organize answers by question
    question_data = []
    for answer in answers:
        if answer.question.question_type == 'rating':
            rating_labels = {
                1: 'Strongly Agree',
                2: 'Agree',
                3: 'Neither Agree nor Disagree',
                4: 'Disagree',
                5: 'Strongly Disagree',
                6: 'Not Applicable'
            }
            question_data.append({
                'question': answer.question.text_en,
                'type': 'rating',
                'value': answer.rating_value,
                'text': rating_labels.get(answer.rating_value, 'N/A')
            })
        else:
            question_data.append({
                'question': answer.question.text_en,
                'type': 'text',
                'value': answer.text_value,
                'text': answer.text_value
            })
    
    context = {
        'survey': survey,
        'question_data': question_data,
        'average_rating': survey.get_average_rating()
    }
    
    return render(request, 'admin_custom/survey_detail.html', context)


@login_required
@user_passes_test(is_admin)
def survey_delete(request, pk):
    """Delete a survey"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        # Delete all related answers first
        Answer.objects.filter(survey=survey).delete()
        # Delete the survey
        survey.delete()
        messages.success(request, 'Survey deleted successfully.')
        return redirect('admin_surveys_list')
    
    return render(request, 'admin_custom/survey_confirm_delete.html', {'survey': survey})


@login_required
@user_passes_test(is_admin)
def assignments_list(request):
    """List all professor-group assignments"""
    assignments = GroupProfessor.objects.select_related('group', 'professor').order_by('group__group_name')
    return render(request, 'admin_custom/assignments_list.html', {'assignments': assignments})


@login_required
@user_passes_test(is_admin)
def assignment_add(request):
    """Assign groups to a professor"""
    if request.method == 'POST':
        professor_id = request.POST.get('professor')
        selected_group_ids = request.POST.getlist('groups')  # Get list of checked group IDs
        
        if not professor_id:
            messages.error(request, 'Please select a professor!')
            return redirect('admin_assignment_add')
        
        professor = get_object_or_404(Professor, pk=professor_id)
        
        # Convert to integers
        selected_group_ids = [int(gid) for gid in selected_group_ids]
        
        # Get current assignments for this professor
        current_assignments = GroupProfessor.objects.filter(professor=professor)
        current_group_ids = set(current_assignments.values_list('group_id', flat=True))
        
        # Determine which to add and which to remove
        to_add = set(selected_group_ids) - current_group_ids
        to_remove = current_group_ids - set(selected_group_ids)
        
        # Add new assignments
        for group_id in to_add:
            group = get_object_or_404(Group, pk=group_id)
            GroupProfessor.objects.create(group=group, professor=professor)
        
        # Remove unchecked assignments
        GroupProfessor.objects.filter(professor=professor, group_id__in=to_remove).delete()
        
        messages.success(request, f'Assignments updated for {professor.full_name}!')
        return redirect('admin_assignments_list')
    
    # GET request
    professors = Professor.objects.all().order_by('full_name')
    groups = Group.objects.all().order_by('group_name')
    
    # Check if professor is pre-selected
    selected_professor_id = request.GET.get('professor')
    assigned_group_ids = []
    
    if selected_professor_id:
        assigned_group_ids = list(
            GroupProfessor.objects.filter(professor_id=selected_professor_id)
            .values_list('group_id', flat=True)
        )
    
    return render(request, 'admin_custom/assignment_form.html', {
        'professors': professors,
        'groups': groups,
        'selected_professor_id': int(selected_professor_id) if selected_professor_id else None,
        'assigned_group_ids': assigned_group_ids,
        'action': 'Manage'
    })


@login_required
@user_passes_test(is_admin)
def assignment_delete(request, pk):
    """Delete assignment"""
    assignment = get_object_or_404(GroupProfessor, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
        return redirect('admin_assignments_list')
    return render(request, 'admin_custom/assignment_confirm_delete.html', {'assignment': assignment})


# Department Management Views
@login_required
@user_passes_test(is_admin)
def departments_list(request):
    """List all departments"""
    departments = Department.objects.select_related('school').all().order_by('school__name', 'name')
    return render(request, 'admin_custom/departments_list.html', {'departments': departments})


@login_required
@user_passes_test(is_admin)
def department_add(request):
    """Add new department"""
    if request.method == 'POST':
        school_id = request.POST.get('school')
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        
        school = get_object_or_404(School, pk=school_id)
        Department.objects.create(
            school=school,
            name=name,
            code=code,
            description=description
        )
        messages.success(request, 'Department added successfully!')
        return redirect('admin_departments_list')
    
    schools = School.objects.all().order_by('name')
    return render(request, 'admin_custom/department_form.html', {'action': 'Add', 'schools': schools})


@login_required
@user_passes_test(is_admin)
def department_edit(request, pk):
    """Edit department"""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        school_id = request.POST.get('school')
        department.school = get_object_or_404(School, pk=school_id)
        department.name = request.POST.get('name')
        department.code = request.POST.get('code')
        department.description = request.POST.get('description', '')
        department.save()
        messages.success(request, 'Department updated successfully!')
        return redirect('admin_departments_list')
    
    schools = School.objects.all().order_by('name')
    return render(request, 'admin_custom/department_form.html', {'department': department, 'action': 'Edit', 'schools': schools})


@login_required
@user_passes_test(is_admin)
def department_delete(request, pk):
    """Delete department"""
    department = get_object_or_404(Department, pk=pk)
    
    # Check if department has related groups or professors
    if department.groups.exists() or department.professors.exists():
        messages.error(request, 'Cannot delete department with existing groups or professors!')
        return redirect('admin_departments_list')
    
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('admin_departments_list')
    
    return render(request, 'admin_custom/department_confirm_delete.html', {'department': department})


# ============================================
# School Management Views
# ============================================

@login_required
@user_passes_test(is_admin)
def schools_list(request):
    """List all schools"""
    schools = School.objects.all().order_by('name')
    return render(request, 'admin_custom/schools_list.html', {'schools': schools})


@login_required
@user_passes_test(is_admin)
def school_add(request):
    """Add new school"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        
        School.objects.create(
            name=name,
            code=code,
            description=description
        )
        messages.success(request, 'School added successfully!')
        return redirect('admin_schools_list')
    
    return render(request, 'admin_custom/school_form.html', {'action': 'Add'})


@login_required
@user_passes_test(is_admin)
def school_edit(request, pk):
    """Edit school"""
    school = get_object_or_404(School, pk=pk)
    
    if request.method == 'POST':
        school.name = request.POST.get('name')
        school.code = request.POST.get('code')
        school.description = request.POST.get('description', '')
        school.save()
        messages.success(request, 'School updated successfully!')
        return redirect('admin_schools_list')
    
    return render(request, 'admin_custom/school_form.html', {'school': school, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin)
def school_delete(request, pk):
    """Delete school"""
    school = get_object_or_404(School, pk=pk)
    
    # Check if school has related departments
    if school.departments.exists():
        messages.error(request, 'Cannot delete school with existing departments!')
        return redirect('admin_schools_list')
    
    if request.method == 'POST':
        school.delete()
        messages.success(request, 'School deleted successfully!')
        return redirect('admin_schools_list')
    
    return render(request, 'admin_custom/school_confirm_delete.html', {'school': school})


# Question Management Views
@login_required
@user_passes_test(is_admin)
def questions_list(request):
    """List all survey questions"""
    questions = Question.objects.all().order_by('order', 'id')
    return render(request, 'admin_custom/questions_list.html', {'questions': questions})


@login_required
@user_passes_test(is_admin)
def question_add(request):
    """Add new question"""
    if request.method == 'POST':
        text_en = request.POST.get('text_en')
        text_uz = request.POST.get('text_uz')
        text_ru = request.POST.get('text_ru')
        question_type = request.POST.get('question_type')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        Question.objects.create(
            text_en=text_en,
            text_uz=text_uz,
            text_ru=text_ru,
            question_type=question_type,
            order=order,
            is_active=is_active
        )
        messages.success(request, 'Question added successfully!')
        return redirect('admin_questions_list')
    
    return render(request, 'admin_custom/question_form.html', {
        'action': 'Add',
        'question': None
    })


@login_required
@user_passes_test(is_admin)
def question_edit(request, pk):
    """Edit question"""
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        question.text_en = request.POST.get('text_en')
        question.text_uz = request.POST.get('text_uz')
        question.text_ru = request.POST.get('text_ru')
        question.question_type = request.POST.get('question_type')
        question.order = request.POST.get('order', 0)
        question.is_active = request.POST.get('is_active') == 'on'
        question.save()
        messages.success(request, 'Question updated successfully!')
        return redirect('admin_questions_list')
    
    return render(request, 'admin_custom/question_form.html', {
        'action': 'Edit',
        'question': question
    })


@login_required
@user_passes_test(is_admin)
def question_delete(request, pk):
    """Delete question"""
    question = get_object_or_404(Question, pk=pk)
    
    # Check if question has answers
    if question.answers.exists():
        messages.error(request, 'Cannot delete question with existing answers!')
        return redirect('admin_questions_list')
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('admin_questions_list')
    
    return render(request, 'admin_custom/question_confirm_delete.html', {'question': question})


# ================================
# Internship Questions Management
# ================================

@login_required
@user_passes_test(is_admin)
def internship_questions_list(request):
    """List all internship questions"""
    questions = InternshipQuestion.objects.all().order_by('order', 'id')
    return render(request, 'admin_custom/internship_questions_list.html', {'questions': questions})


@login_required
@user_passes_test(is_admin)
def internship_question_add(request):
    """Add new internship question"""
    if request.method == 'POST':
        text_en = request.POST.get('text_en')
        text_uz = request.POST.get('text_uz')
        text_ru = request.POST.get('text_ru')
        question_type = request.POST.get('question_type')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        InternshipQuestion.objects.create(
            text_en=text_en,
            text_uz=text_uz,
            text_ru=text_ru,
            question_type=question_type,
            order=order,
            is_active=is_active
        )
        messages.success(request, 'Internship question added successfully!')
        return redirect('admin_internship_questions_list')
    
    return render(request, 'admin_custom/internship_question_form.html', {
        'action': 'Add',
        'question': None
    })


@login_required
@user_passes_test(is_admin)
def internship_question_edit(request, pk):
    """Edit internship question"""
    question = get_object_or_404(InternshipQuestion, pk=pk)
    if request.method == 'POST':
        question.text_en = request.POST.get('text_en')
        question.text_uz = request.POST.get('text_uz')
        question.text_ru = request.POST.get('text_ru')
        question.question_type = request.POST.get('question_type')
        question.order = request.POST.get('order', 0)
        question.is_active = request.POST.get('is_active') == 'on'
        question.save()
        messages.success(request, 'Internship question updated successfully!')
        return redirect('admin_internship_questions_list')
    
    return render(request, 'admin_custom/internship_question_form.html', {
        'action': 'Edit',
        'question': question
    })


@login_required
@user_passes_test(is_admin)
def internship_question_delete(request, pk):
    """Delete internship question"""
    question = get_object_or_404(InternshipQuestion, pk=pk)
    
    # Check if question has answers
    if question.answers.exists():
        messages.error(request, 'Cannot delete question with existing answers!')
        return redirect('admin_internship_questions_list')
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Internship question deleted successfully!')
        return redirect('admin_internship_questions_list')
    
    return render(request, 'admin_custom/internship_question_confirm_delete.html', {'question': question})


@login_required
@user_passes_test(is_admin)
def internship_surveys_list(request):
    """List all internship surveys"""
    surveys = InternshipSurvey.objects.select_related('group').order_by('-created_at')
    return render(request, 'admin_custom/internship_surveys_list.html', {'surveys': surveys})


@login_required
@user_passes_test(is_admin)
def internship_survey_detail(request, pk):
    """View internship survey detail"""
    survey = get_object_or_404(InternshipSurvey, pk=pk)
    
    # Get all answers for this survey
    answers = InternshipAnswer.objects.filter(internship_survey=survey).select_related('question').order_by('question__order')
    
    # Organize answers by question
    question_data = []
    for answer in answers:
        if answer.question.question_type == 'rating':
            rating_labels = {
                1: 'Strongly Agree',
                2: 'Agree',
                3: 'Neither Agree nor Disagree',
                4: 'Disagree',
                5: 'Strongly Disagree',
                6: 'Not Applicable'
            }
            question_data.append({
                'question': answer.question.text_en,
                'type': 'rating',
                'value': answer.rating_value,
                'text': rating_labels.get(answer.rating_value, 'N/A')
            })
        else:
            question_data.append({
                'question': answer.question.text_en,
                'type': 'text',
                'value': answer.text_value,
                'text': answer.text_value
            })
    
    context = {
        'survey': survey,
        'question_data': question_data,
        'average_rating': survey.get_average_rating()
    }
    
    return render(request, 'admin_custom/internship_survey_detail.html', context)


@login_required
@user_passes_test(is_admin)
def internship_survey_delete(request, pk):
    """Delete an internship survey"""
    survey = get_object_or_404(InternshipSurvey, pk=pk)
    
    if request.method == 'POST':
        # Delete all related answers first
        InternshipAnswer.objects.filter(internship_survey=survey).delete()
        # Delete the survey
        survey.delete()
        messages.success(request, 'Internship survey deleted successfully.')
        return redirect('admin_internship_surveys_list')
    
    return render(request, 'admin_custom/internship_survey_confirm_delete.html', {'survey': survey})


@login_required
@user_passes_test(is_admin)
def admin_professors_rating(request):
    """Professors rating report with detailed question averages"""
    from django.db.models import Avg, Count
    
    # Get all questions ordered by their order field
    questions = Question.objects.filter(is_active=True, question_type='rating').order_by('order')
    text_question = Question.objects.filter(is_active=True, question_type='text').first()
    
    # Get all professors
    professors = Professor.objects.all()
    
    professors_data = []
    
    for professor in professors:
        # Get all surveys for this professor
        surveys = Survey.objects.filter(professor=professor)
        
        if not surveys.exists():
            continue
        
        professor_row = {
            'professor': professor,
            'question_averages': [],
            'comments': []
        }
        
        # Calculate average for each rating question
        total_sum = 0
        valid_question_count = 0
        
        for question in questions:
            # Get all answers for this question and professor (excluding N/A)
            answers = Answer.objects.filter(
                survey__professor=professor,
                question=question,
                rating_value__isnull=False
            ).exclude(rating_value=6)  # Exclude N/A
            
            if answers.exists():
                avg = answers.aggregate(Avg('rating_value'))['rating_value__avg']
                professor_row['question_averages'].append(round(avg, 2) if avg else 0)
                total_sum += avg if avg else 0
                valid_question_count += 1
            else:
                professor_row['question_averages'].append(0)
        
        # Calculate overall average
        professor_row['overall_average'] = round(total_sum / valid_question_count, 2) if valid_question_count > 0 else 0
        
        # Get text comments (Q20)
        if text_question:
            comments = Answer.objects.filter(
                survey__professor=professor,
                question=text_question,
                text_value__isnull=False
            ).exclude(text_value='').values_list('text_value', flat=True)
            professor_row['comments'] = list(comments)
        
        professors_data.append(professor_row)
    
    # Sort by overall average (ascending - lower is better since 1 is best)
    professors_data.sort(key=lambda x: x['overall_average'])
    
    context = {
        'professors_data': professors_data,
        'questions': questions,
        'text_question': text_question,
    }
    
    return render(request, 'admin_custom/professors_rating.html', context)
