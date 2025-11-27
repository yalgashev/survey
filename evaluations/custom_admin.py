from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.db.models import Count, Avg
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from .models import Group, Professor, Survey

class CustomAdminSite(admin.AdminSite):
    site_header = _('Student Evaluation System')
    site_title = _('Admin Dashboard')
    index_title = _('Dashboard')
    
    def index(self, request, extra_context=None):
        """
        Custom admin index view with dashboard
        """
        # Get statistics
        total_groups = Group.objects.count()
        total_professors = Professor.objects.count()
        total_surveys = Survey.objects.count()
        total_students_participated = Group.objects.aggregate(
            total=Count('participated_students')
        )['total'] or 0
        
        # Recent surveys (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_surveys = Survey.objects.filter(created_at__gte=week_ago).count()
        
        # Top rated professors (average rating <= 2.5)
        top_professors = []
        for prof in Professor.objects.all()[:5]:
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
                        'professor': prof,
                        'rating': round(avg_rating, 2),
                        'count': surveys.count()
                    })
        
        # Sort by rating (lower is better)
        top_professors.sort(key=lambda x: x['rating'])
        top_professors = top_professors[:5]
        
        # Groups with highest participation
        top_groups = Group.objects.filter(total_students__gt=0).annotate(
            participation_rate=Count('participated_students')
        ).order_by('-participation_rate')[:5]
        
        # Recent activity
        recent_activity = Survey.objects.select_related('group', 'professor').order_by('-created_at')[:10]
        
        # Get the default admin context
        app_list = self.get_app_list(request)
        
        context = {
            **self.each_context(request),
            'total_groups': total_groups,
            'total_professors': total_professors,
            'total_surveys': total_surveys,
            'total_students_participated': total_students_participated,
            'recent_surveys': recent_surveys,
            'top_professors': top_professors,
            'top_groups': top_groups,
            'recent_activity': recent_activity,
            'title': self.index_title,
            'app_list': app_list,
            'has_permission': self.has_permission(request),
        }
        
        if extra_context:
            context.update(extra_context)
        
        request.current_app = self.name
        return render(request, 'admin/custom_dashboard.html', context)

# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')
