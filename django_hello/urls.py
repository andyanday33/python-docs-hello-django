from django.contrib import admin
from django.urls import include, path
from django.urls import reverse
from .views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('', homepage_view, name='homepage' ),
    path('i/dashboard/', InstructorDashboardView.as_view(), name='insturctor_dashboard'),
    path('s/dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),

    # instructor views
    path('i/exams/', ExamListView.as_view(), name='exam_list'),
    path('i/exams/create/', ExamCreateView.as_view(), name='exam_create'),
    path('i/exams/<int:exam_pk>/', ExamDetailView.as_view(), name='exam_detail'),
    path('i/exams/<int:exam_pk>/students/', add_student_to_exam_view, name='add_student_to_exam'),
    path('i/exams/<int:exam_pk>/student/<int:student_pk>/delete/', delete_student_exam_access_view, name='add_student_to_exam'),
    path('i/exams/<int:exam_pk>/question/<int:question_pk>/', question_detail_view, name='question_detail'),
    path('i/exams/<int:exam_pk>/question/<int:question_pk>/delete/', question_delete_view, name='question_delete'),
    path('i/exams/<int:exam_pk>/question/<int:question_pk>/choice/<int:choice_pk>/delete/', question_choice_delete_view, name='question_choice_delete'),
    path('i/exams/<int:exam_pk>/question/<int:question_pk>/choice/<int:choice_pk>/toggle_true/', question_toggle_true_view, name='question_choice_toggle'),
    path('i/exams/<int:exam_pk>/add-question/', QuestionCreateView.as_view(), name='question_add'),

    path('s/exams/', student_exam_list_view, name='student_exam_list'),
    path('s/exams/<int:exam_pk>/', student_exam_detail_view, name='student_exam_detail'),
    path('s/exams/<int:exam_pk>/answer/<int:question_pk>/', question_answer_view, name='question_answer'),

    # student views


    path('logout/', logout_view , name='mylogout'),
]



