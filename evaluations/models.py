from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class School(models.Model):
    """School/Faculty model"""
    name = models.CharField(max_length=200, unique=True, verbose_name=_('School Name'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('School Code'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(models.Model):
    """Department model - belongs to a School"""
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name='departments',
        verbose_name=_('School')
    )
    name = models.CharField(max_length=200, verbose_name=_('Department Name'))
    code = models.CharField(max_length=50, verbose_name=_('Department Code'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['school__name', 'name']
        unique_together = [['school', 'name'], ['school', 'code']]

    def __str__(self):
        return f"{self.school.name} - {self.name} ({self.code})"


class Group(models.Model):
    """Academic group/class model"""
    SEMESTER_CHOICES = [
        (1, _('Semester 1 (1st year, Sep-Feb)')),
        (2, _('Semester 2 (1st year, Mar-May)')),
        (3, _('Semester 3 (2nd year, Sep-Feb)')),
        (4, _('Semester 4 (2nd year, Mar-May)')),
        (5, _('Semester 5 (3rd year, Sep-Feb)')),
        (6, _('Semester 6 (3rd year, Mar-May)')),
        (7, _('Semester 7 (4th year, Sep-Feb)')),
        (8, _('Semester 8 (4th year, Mar-May)')),
    ]
    
    group_name = models.CharField(max_length=100, unique=True, verbose_name=_('Group Name'))
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='groups',
        verbose_name=_('Department')
    )
    semester = models.IntegerField(
        choices=SEMESTER_CHOICES,
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        verbose_name=_('Semester')
    )
    total_students = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Students')
    )
    participated_students = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Participated Students')
    )

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        ordering = ['group_name']

    def __str__(self):
        return f"{self.group_name} - {self.department.name} (Semester {self.semester})"


class Professor(models.Model):
    """Professor/Instructor model"""
    full_name = models.CharField(max_length=200, verbose_name=_('Full Name'))
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name='professors',
        verbose_name=_('School')
    )
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'))
    groups = models.ManyToManyField(
        Group,
        through='GroupProfessor',
        related_name='professors',
        verbose_name=_('Groups')
    )

    class Meta:
        verbose_name = _('Professor')
        verbose_name_plural = _('Professors')
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.school.name})"


class GroupProfessor(models.Model):
    """Assignment of professors to groups"""
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='group_professors',
        verbose_name=_('Group')
    )
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name='professor_groups',
        verbose_name=_('Professor')
    )

    class Meta:
        verbose_name = _('Group-Professor Assignment')
        verbose_name_plural = _('Group-Professor Assignments')
        unique_together = ['group', 'professor']
        ordering = ['group', 'professor']

    def __str__(self):
        return f"{self.group.group_name} - {self.professor.full_name}"


class Question(models.Model):
    """Survey question with multi-language support"""
    
    QUESTION_TYPE_CHOICES = [
        ('rating', _('Rating (1-6)')),
        ('text', _('Text (Open-ended)')),
    ]
    
    # Question text in three languages
    text_en = models.TextField(verbose_name=_('Question Text (English)'))
    text_uz = models.TextField(verbose_name=_('Question Text (Uzbek)'))
    text_ru = models.TextField(verbose_name=_('Question Text (Russian)'))
    
    # Question type
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='rating',
        verbose_name=_('Question Type')
    )
    
    # Order/sequence
    order = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Order')
    )
    
    # Active status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Survey Question')
        verbose_name_plural = _('Survey Questions')
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Q{self.order}: {self.text_en[:50]}..."
    
    def get_text(self, language='en'):
        """Get question text in specified language"""
        if language == 'uz':
            return self.text_uz
        elif language == 'ru':
            return self.text_ru
        return self.text_en


class Survey(models.Model):
    """Survey session - represents one student evaluating one professor"""
    
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name=_('Group')
    )
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name=_('Professor')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Survey Session')
        verbose_name_plural = _('Survey Sessions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.group.group_name} - {self.professor.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_average_rating(self):
        """Calculate average rating from all rating-type answers"""
        rating_answers = self.answers.filter(
            question__question_type='rating'
        ).exclude(rating_value=6)  # Exclude N/A
        
        if rating_answers.exists():
            total = sum(answer.rating_value for answer in rating_answers)
            return total / rating_answers.count()
        return 0


class Answer(models.Model):
    """Student's answer to a survey question"""
    
    # Rating choices (1=best, 5=worst, 6=N/A)
    RATING_CHOICES = [
        (1, _('Strongly Agree')),
        (2, _('Agree')),
        (3, _('Neither Agree nor Disagree')),
        (4, _('Disagree')),
        (5, _('Strongly Disagree')),
        (6, _('Not Applicable')),
    ]
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Survey')
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Question')
    )
    
    # For rating questions (1-6)
    rating_value = models.IntegerField(
        null=True,
        blank=True,
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name=_('Rating Value')
    )
    
    # For text questions
    text_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Text Answer')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Survey Answer')
        verbose_name_plural = _('Survey Answers')
        unique_together = ['survey', 'question']
        ordering = ['question__order']
    
    def __str__(self):
        if self.question.question_type == 'rating':
            return f"{self.survey} - Q{self.question.order}: {self.rating_value}"
        return f"{self.survey} - Q{self.question.order}: {self.text_value[:30]}..."


# ================================
# Internship Evaluation Models
# ================================

class InternshipQuestion(models.Model):
    """Questions for internship evaluation (multilingual)"""
    QUESTION_TYPE_CHOICES = [
        ('rating', _('Rating (1-6)')),
        ('text', _('Text Answer')),
    ]
    
    text_en = models.TextField(verbose_name=_('Question Text (English)'))
    text_uz = models.TextField(verbose_name=_('Question Text (Uzbek)'))
    text_ru = models.TextField(verbose_name=_('Question Text (Russian)'))
    
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='rating',
        verbose_name=_('Question Type')
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name=_('Display Order'),
        help_text=_('Order in which this question appears')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
        help_text=_('Only active questions will be shown in surveys')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Internship Question')
        verbose_name_plural = _('Internship Questions')
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Q{self.order}: {self.text_en[:50]}..."
    
    def get_text(self, language='en'):
        """Get question text in specified language"""
        if language == 'uz':
            return self.text_uz
        elif language == 'ru':
            return self.text_ru
        return self.text_en


class InternshipSurvey(models.Model):
    """Internship evaluation survey session"""
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='internship_surveys',
        verbose_name=_('Group')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Completed At'))
    
    class Meta:
        verbose_name = _('Internship Survey')
        verbose_name_plural = _('Internship Surveys')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Internship Survey - {self.group.group_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_average_rating(self):
        """Calculate average rating for this internship survey"""
        ratings = self.internship_answers.filter(
            question__question_type='rating',
            rating_value__isnull=False
        ).exclude(rating_value=6)  # Exclude "Not Applicable"
        
        if ratings.exists():
            avg = ratings.aggregate(models.Avg('rating_value'))['rating_value__avg']
            return round(avg, 2) if avg else 0
        return 0


class InternshipAnswer(models.Model):
    """Student's answer to an internship question"""
    RATING_CHOICES = [
        (1, _('Strongly Agree')),
        (2, _('Agree')),
        (3, _('Neither Agree nor Disagree')),
        (4, _('Disagree')),
        (5, _('Strongly Disagree')),
        (6, _('Not Applicable')),
    ]
    
    internship_survey = models.ForeignKey(
        InternshipSurvey,
        on_delete=models.CASCADE,
        related_name='internship_answers',
        verbose_name=_('Internship Survey')
    )
    question = models.ForeignKey(
        InternshipQuestion,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Question')
    )
    
    # For rating questions (1-6)
    rating_value = models.IntegerField(
        null=True,
        blank=True,
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name=_('Rating Value')
    )
    
    # For text questions
    text_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Text Answer')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Internship Answer')
        verbose_name_plural = _('Internship Answers')
        unique_together = ['internship_survey', 'question']
        ordering = ['question__order']
    
    def __str__(self):
        if self.question.question_type == 'rating':
            return f"{self.internship_survey} - Q{self.question.order}: {self.rating_value}"
        return f"{self.internship_survey} - Q{self.question.order}: {self.text_value[:30]}..."
