from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Survey, Group, Question, Answer, InternshipQuestion, InternshipAnswer


class GroupSelectionForm(forms.Form):
    """Form for selecting academic group and language"""
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label=_('Select your group'),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'required': True,
            'autocomplete': 'off',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false',
            'data-form-type': 'other',  # Prevent iOS password/credit card autofill
            'data-lpignore': 'true',  # Ignore LastPass
        }),
        label=_('Academic Group')
    )
    
    language = forms.ChoiceField(
        choices=[
            ('en', 'English'),
            ('uz', 'O\'zbek'),
            ('ru', 'Русский')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'required': True
        }),
        label=_('Preferred Language'),
        initial='en'
    )


class QuestionForm(forms.ModelForm):
    """Form for creating/editing survey questions in admin"""
    
    class Meta:
        model = Question
        fields = ['text_en', 'text_uz', 'text_ru', 'question_type', 'order', 'is_active']
        widgets = {
            'text_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'text_uz': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'text_ru': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DynamicSurveyForm(forms.Form):
    """Dynamic form for survey - fields created based on active questions"""
    
    def __init__(self, *args, language='en', **kwargs):
        super().__init__(*args, **kwargs)
        self.language = language
        
        # Get all active questions ordered
        questions = Question.objects.filter(is_active=True).order_by('order')
        
        for question in questions:
            field_name = f'question_{question.id}'
            
            if question.question_type == 'rating':
                # Rating question (1-6)
                self.fields[field_name] = forms.ChoiceField(
                    choices=Answer.RATING_CHOICES,
                    widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
                    label=question.get_text(language),
                    required=True
                )
            else:
                # Text question
                self.fields[field_name] = forms.CharField(
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 4,
                        'placeholder': _('Your answer...')
                    }),
                    label=question.get_text(language),
                    required=False
                )


class DynamicInternshipSurveyForm(forms.Form):
    """Dynamic form for internship survey - fields created based on active internship questions"""
    
    def __init__(self, *args, language='en', **kwargs):
        super().__init__(*args, **kwargs)
        self.language = language
        
        # Get all active internship questions ordered
        questions = InternshipQuestion.objects.filter(is_active=True).order_by('order')
        
        for question in questions:
            field_name = f'question_{question.id}'
            
            if question.question_type == 'rating':
                # Rating question (1-6)
                self.fields[field_name] = forms.ChoiceField(
                    choices=InternshipAnswer.RATING_CHOICES,
                    widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
                    label=question.get_text(language),
                    required=True
                )
            else:
                # Text question
                self.fields[field_name] = forms.CharField(
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 4,
                        'placeholder': _('Your answer...')
                    }),
                    label=question.get_text(language),
                    required=False
                )


# Keep old forms for backward compatibility during migration
class SurveyForm(forms.Form):
    """Placeholder - replaced by DynamicSurveyForm"""
    pass


class SurveyEditForm(forms.Form):
    """Placeholder - will be replaced with dynamic editing"""
    pass
