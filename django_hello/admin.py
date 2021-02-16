from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(OEAUser)
admin.site.register(AnsweredQuestion)
admin.site.register(Question)
admin.site.register(QuestionChoice)
admin.site.register(Exam)
admin.site.register(StudentExamAccess)