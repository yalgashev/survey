from django.contrib import admin
from django.db.models import Avg, Count, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Group, Professor, GroupProfessor, Survey, Question, Answer
from .custom_admin import custom_admin_site


class GroupProfessorInline(admin.TabularInline):
    """Inline for assigning professors to groups"""
    model = GroupProfessor
    extra = 1
    autocomplete_fields = ['professor']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'department', 'total_students', 'participated_students', 'participation_rate']
    list_filter = ['department']
    search_fields = ['group_name', 'department']
    inlines = [GroupProfessorInline]
    
    def participation_rate(self, obj):
        if obj.total_students > 0:
            rate = (obj.participated_students / obj.total_students) * 100
            color = 'green' if rate >= 70 else 'orange' if rate >= 50 else 'red'
            return format_html(
                '<span style="color: {};">{}</span>',
                color, f'{rate:.1f}%'
            )
        return '0%'
    participation_rate.short_description = _('Participation Rate')


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'school', 'groups_count', 'surveys_count', 'average_rating', 'view_analytics']
    list_filter = ['school']
    search_fields = ['full_name', 'school__name']
    inlines = [GroupProfessorInline]
    
    def groups_count(self, obj):
        return obj.groups.count()
    groups_count.short_description = _('Groups')
    
    def surveys_count(self, obj):
        return obj.surveys.count()
    surveys_count.short_description = _('Total Surveys')
    
    def average_rating(self, obj):
        surveys = obj.surveys.all()
        if not surveys:
            return 'N/A'
        
        total = 0
        count = 0
        for survey in surveys:
            avg = survey.get_average_rating()
            if avg > 0:
                total += avg
                count += 1
        
        if count > 0:
            avg = total / count
            color = 'green' if avg <= 2 else 'orange' if avg <= 3.5 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
                color, avg
            )
        return 'N/A'
    average_rating.short_description = _('Avg Rating')
    
    def view_analytics(self, obj):
        url = reverse('admin:evaluations_professor_analytics', args=[obj.pk])
        return format_html('<a href="{}" class="button">View Analytics</a>', url)
    view_analytics.short_description = _('Analytics')
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:professor_id>/analytics/',
                self.admin_site.admin_view(self.professor_analytics_view),
                name='evaluations_professor_analytics',
            ),
        ]
        return custom_urls + urls
    
    def professor_analytics_view(self, request, professor_id):
        from django.shortcuts import render, get_object_or_404
        
        professor = get_object_or_404(Professor, pk=professor_id)
        
        # Get all surveys for this professor grouped by group
        groups_data = []
        for group in professor.groups.all():
            surveys = Survey.objects.filter(professor=professor, group=group)
            if surveys.exists():
                # Calculate averages for each question
                question_averages = {}
                for i in range(1, 20):
                    q_field = f'q{i}'
                    # Exclude N/A (6) from averages
                    valid_surveys = surveys.exclude(**{q_field: 6})
                    if valid_surveys.exists():
                        avg = valid_surveys.aggregate(avg=Avg(q_field))['avg']
                        question_averages[f'q{i}'] = round(avg, 2) if avg else None
                    else:
                        question_averages[f'q{i}'] = None
                
                # Get all comments
                comments = surveys.exclude(q20_comment__isnull=True).exclude(q20_comment='').values_list('q20_comment', flat=True)
                
                # Overall average
                overall_ratings = []
                for survey in surveys:
                    avg = survey.get_average_rating()
                    if avg > 0:
                        overall_ratings.append(avg)
                
                overall_avg = sum(overall_ratings) / len(overall_ratings) if overall_ratings else None
                
                groups_data.append({
                    'group': group,
                    'survey_count': surveys.count(),
                    'question_averages': question_averages,
                    'overall_average': round(overall_avg, 2) if overall_avg else None,
                    'comments': list(comments),
                })
        
        context = {
            'professor': professor,
            'groups_data': groups_data,
            'title': f'Analytics for {professor.full_name}',
        }
        
        return render(request, 'admin/professor_analytics.html', context)


@admin.register(GroupProfessor)
class GroupProfessorAdmin(admin.ModelAdmin):
    list_display = ['group', 'professor']
    list_filter = ['group', 'professor']
    search_fields = ['group__group_name', 'professor__full_name']
    autocomplete_fields = ['group', 'professor']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['order', 'text_en_preview', 'question_type', 'is_active', 'created_at']
    list_filter = ['question_type', 'is_active']
    search_fields = ['text_en', 'text_uz', 'text_ru']
    list_editable = ['is_active']
    ordering = ['order', 'id']
    
    fieldsets = (
        (_('Question Text'), {
            'fields': ('text_en', 'text_uz', 'text_ru')
        }),
        (_('Settings'), {
            'fields': ('question_type', 'order', 'is_active')
        }),
    )
    
    def text_en_preview(self, obj):
        return obj.text_en[:80] + '...' if len(obj.text_en) > 80 else obj.text_en
    text_en_preview.short_description = _('Question (English)')


class AnswerInline(admin.TabularInline):
    """Inline for viewing answers in survey"""
    model = Answer
    extra = 0
    can_delete = False
    readonly_fields = ['question', 'rating_value', 'text_value']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['professor', 'group', 'created_at', 'answers_count', 'average_rating_display']
    list_filter = ['created_at', 'professor', 'group']
    search_fields = ['professor__full_name', 'group__group_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    inlines = [AnswerInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('group', 'professor', 'created_at')
        }),
    )
    
    def answers_count(self, obj):
        return obj.answers.count()
    answers_count.short_description = _('Answers')
    
    def average_rating_display(self, obj):
        avg = obj.get_average_rating()
        if avg > 0:
            color = 'green' if avg <= 2 else 'orange' if avg <= 3.5 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
                color, avg
            )
        return 'N/A'
    average_rating_display.short_description = _('Avg Rating')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['survey', 'question_preview', 'get_answer_value', 'created_at']
    list_filter = ['question__question_type', 'created_at']
    search_fields = ['survey__professor__full_name', 'survey__group__group_name', 'text_value']
    readonly_fields = ['survey', 'question', 'created_at']
    
    def question_preview(self, obj):
        return obj.question.text_en[:50] + '...' if len(obj.question.text_en) > 50 else obj.question.text_en
    question_preview.short_description = _('Question')
    
    def get_answer_value(self, obj):
        if obj.question.question_type == 'rating':
            return f'{obj.rating_value} - {obj.get_rating_value_display()}'
        return obj.text_value[:50] if obj.text_value else ''
    get_answer_value.short_description = _('Answer')


# Register models with both default and custom admin sites
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Professor, ProfessorAdmin)
custom_admin_site.register(GroupProfessor, GroupProfessorAdmin)
custom_admin_site.register(Survey, SurveyAdmin)
custom_admin_site.register(Question, QuestionAdmin)
custom_admin_site.register(Answer, AnswerAdmin)

# Customize admin site header
admin.site.site_header = _('Student-Professor Evaluation System')
admin.site.site_title = _('Evaluation Admin')
admin.site.index_title = _('Administration')

custom_admin_site.site_header = _('Student Evaluation System')
custom_admin_site.site_title = _('Admin Dashboard')
custom_admin_site.index_title = _('Dashboard')
