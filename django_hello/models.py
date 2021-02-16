from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import IntEnum

class UserTypes(IntEnum):
    STUDENT = 1
    INSTRUCTOR = 2
    ADMIN = 3

class OEAUser(AbstractUser):

    
    USER_TYPE_CHOICES = (
        (1, 'STUDENT'),
        (2, 'INSTRUCTOR'),
        (3, 'ADMIN'),
    )
    user_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=USER_TYPE_CHOICES)
    email = models.EmailField()
    
class StudentExamAccess(models.Model):
    student = models.ForeignKey('OEAUser', null=True, blank=True, on_delete=models.CASCADE)
    exam = models.ForeignKey('Exam', null=True, blank=True, on_delete=models.CASCADE)
    has_attended = models.BooleanField(null=True, blank=True, default=False)
    score = models.FloatField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class AnsweredQuestion(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE) 
    answer_choice = models.ForeignKey('QuestionChoice', null=True, blank=True, on_delete=models.CASCADE)
    student = models.ForeignKey('OEAUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class QuestionChoice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_true_choice = models.BooleanField(null=True, blank=True, default=False)

    def __str__(self) -> str:
        return f'Q{self.question.pk}/QC{self.pk} - {self.text}'

class Question(models.Model):
    question_text = models.CharField(max_length=500)
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'E{self.exam.pk}Q{self.pk} - {self.question_text}'

    def __str__(self):
        return f"Q({self.pk}): {self.question_text}"


class Exam(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1000)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    instructor = models.ForeignKey('OEAUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exam {self.name}"


