from django import forms
from django.forms import fields
from .models import * 
from django.contrib.admin import widgets   

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
                    'start_date': forms.widgets.DateTimeInput(),
                    'end_date': forms.widgets.DateTimeInput()
                }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']
        widgets = {

        }

class QuestionChoiceForm(forms.ModelForm):
    class Meta:
        model = QuestionChoice
        fields = ['text', 'is_true_choice']
        widgets = {
        }

class StudentExamAccessForm(forms.ModelForm):
    class Meta:
        model = StudentExamAccess
        fields = ['student']
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        super(StudentExamAccessForm, self).__init__(*args, **kwargs)
        self.fields['student'].queryset = OEAUser.objects.filter(user_type__in=[UserTypes.STUDENT])



class AnsweredQuestionForm(forms.ModelForm):
    class Meta:
        model = AnsweredQuestion
        fields = ['answer_choice']
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question', None)
        super(AnsweredQuestionForm, self).__init__(*args, **kwargs)
        # old_queryset = self.fields['answer_choice'].queryset
        choices = QuestionChoice.objects.filter(question=self.question).order_by('id')
        self.fields['answer_choice'].queryset = choices