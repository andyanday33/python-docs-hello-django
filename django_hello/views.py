from datetime import date
from multiprocessing import context
from string import Template
from django.db.models.query_utils import Q
from django.forms import utils
from django.shortcuts import render
from django.contrib.auth.views import LoginView

from django.shortcuts import render,redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, response, HttpResponse
from .models import *
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, FormView
from .forms import *
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

def validate_instuctor(request):
    return request.user.user_type == UserTypes.INSTRUCTOR

def validate_student(request):
    return request.user.user_type == UserTypes.STUDENT


def homepage_view(request):
    if  isinstance(request.user, AnonymousUser):
        context={'user_type': 'anon'}
    else:
        context={'user_type': request.user.user_type}

    return render(request, 'core/homepage.html', context)
 
 #? implement this
class InstructorDashboardView(TemplateView):
    template_name = 'core/instructor_dashboard.html'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

 #? implement this
class StudentDashboardView(TemplateView):
    template_name = ''
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
        

class ExamListView(ListView):
    template_name = 'core/exam_list.html'
    model = Exam
    context_object_name = 'exams'



       
class ExamDetailView(DetailView):
    template_name = 'core/exam_detail.html'
    model  = Exam
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        return context
        
class ExamCreateView(CreateView):
    model = Exam
    template_name = 'core/exam_create.html'
    form_class = ExamForm
    success_url = reverse_lazy('exam_list')

    def form_valid(self, form):
        data = form.cleaned_data 
        user = self.request.user
        if form.is_valid():
            if user.user_type == UserTypes.INSTRUCTOR:
                Exam.objects.create(
                    **data,
                    instructor=user
                )
                return HttpResponseRedirect(reverse_lazy('exam_list'))
            else:
                raise PermissionDenied("You are not an Instructor.")    


class QuestionCreateView(FormView):
    model = Question
    template_name = 'core/question_create.html'
    form_class = QuestionForm
    success_url = reverse_lazy('exam_list')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam_pk'] = self.kwargs.get('exam_pk')
        return context


    def form_valid(self, form):
        data = form.cleaned_data 
        user = self.request.user
        if form.is_valid():
            exam_pk = self.kwargs.get('exam_pk')
            if user.user_type == UserTypes.INSTRUCTOR:    
                created_question = Question.objects.create(
                    **data,
                    exam=Exam.objects.get(pk=exam_pk),
                )
                return HttpResponseRedirect(reverse_lazy('exam_detail', args=[exam_pk]))
            else:
                raise PermissionDenied("You are not an Instructor.")    


class QuestionListView(ListView):
    template_name = 'core/question_list.html'
    model = Question
    context_object_name = 'question'

def question_choice_delete_view(request, exam_pk, question_pk, choice_pk):
    # delete the question choice
    deleted = QuestionChoice.objects.get(pk=choice_pk).delete()
    print(deleted)
    # redirect to the question_detail_view
    return HttpResponseRedirect(reverse_lazy('question_detail', args=[exam_pk, question_pk])) 

def question_delete_view(request, exam_pk, question_pk):
    # delete the question choice
    Question.objects.get(pk=question_pk).delete()
    # redirect to the question_detail_view
    return HttpResponseRedirect(reverse_lazy('exam_detail', args=[exam_pk])) 

def question_toggle_true_view(request, exam_pk, question_pk, choice_pk):
    # delete the question choice
    qc = QuestionChoice.objects.get(pk=choice_pk)
    all_other_choices = QuestionChoice.objects.filter(question__pk=question_pk)
    should_toggle = True
    if not qc.is_true_choice:
        # tries to make it true
        if any([qc.is_true_choice for qc in all_other_choices]):
            should_toggle = False # can't make 2 questions true

    if should_toggle:
        qc.is_true_choice = not qc.is_true_choice
        qc.save()
    # redirect to the question_detail_view
    return HttpResponseRedirect(reverse_lazy('question_detail', args=[exam_pk, question_pk])) 


def question_answer_view(request, exam_pk, question_pk):
    from django.utils import timezone
    from django.contrib import messages

    context = {}
    now = timezone.now()
    exam = Exam.objects.get(pk=exam_pk)
    exam_questions = Question.objects.filter(exam=exam).order_by('id')
    question = Question.objects.get(pk=question_pk)
    choices = QuestionChoice.objects.filter(question=question).order_by('id')
    try:
        answered_question = AnsweredQuestion.objects.filter(student=request.user, question=question).first()
    except:
        answered_question = []
    context['exam'] = exam
    context['question'] = question
    context['choices'] = choices
    context['previous_answer'] = None
    next_question = None
    
    try:
        if answered_question.answer_choice:
            context['form'] = AnsweredQuestionForm(instance=answered_question, question=question)
        else:
            context['form'] = AnsweredQuestionForm( question=question)
    except:
        context['form'] = AnsweredQuestionForm( question=question)

    
    for i, eq in enumerate(exam_questions):
        if eq == question:
            if i < len(exam_questions) - 1:
                # sonuncu soru değil
                next_question = exam_questions[i+1]
            break
        
    context['next_url'] = None


    if next_question is not None:
        # find out next url
        next_url = reverse('question_answer', args=[exam_pk, next_question.pk])
        context['next_url'] = next_url
    else:
        #finish exam
        #! update the score if the time is right
        messages.success(request, 'You have finished your exam.')
        next_url = reverse('student_exam_detail', args=[exam_pk])
        context['next_url'] = next_url
    

    if request.method == 'POST':
        # create answered question 
        form = AnsweredQuestionForm(request.POST, question=question)
        
        print('form valid', form.is_valid())
        if form.is_valid():
            data = form.cleaned_data
            selected_choice = data.get('answer_choice')
            try:
                if answered_question.answer_choice:
                    answered_question.answer_choice = selected_choice
                    answered_question.save()
                    messages.success(request, 'You have submitted your answer! ')
                else:
                    AnsweredQuestion.objects.create(
                        question=question,
                        answer_choice=selected_choice,
                        student=request.user
                    )
                    messages.success(request, 'You have submitted your answer! ')

            except:
                AnsweredQuestion.objects.create(
                    question=question,
                    answer_choice=selected_choice,
                    student=request.user
                )
                messages.success(request, 'You have submitted your answer! ')

        try:
            if answered_question.answer_choice:
                context['form'] = AnsweredQuestionForm(instance=answered_question, question=question)
            else:
                context['form'] = AnsweredQuestionForm( question=question)
        except:
                context['form'] = AnsweredQuestionForm( question=question)

    return render(request, 'core/answer_question.html', context)


def student_exam_detail_view(request, exam_pk):
    from django.utils import timezone
    context = {}
    now = timezone.now()
    exam = Exam.objects.get(pk=exam_pk)
    student = request.user
    is_exam_active = exam.start_date<=now<=exam.end_date
    msg = ""
    has_answered = False

    exam_questions = exam.question_set.all()
    answers = AnsweredQuestion.objects.filter(question__in=exam_questions, student=student)
    context['answers'] = answers 
    context['score'] = 0 
    if answers: # cevapları var
        has_answered = True
        exam_correctness = []
        for eq in exam_questions:
            # get the AnsweredQuestion
            aq = answers.filter(question=eq).first()
            setattr(eq, 'is_answer_true', aq.answer_choice.is_true_choice)
            setattr(eq, 'student_answer', aq.answer_choice)
            correct_qc = QuestionChoice.objects.filter(question=eq, is_true_choice=True).first()
            setattr(eq, 'correct_answer', correct_qc)
            exam_correctness.append(aq.answer_choice.is_true_choice)


        context['score'] = sum(exam_correctness)/len(exam_questions)*100
        
    context['exam_questions'] = exam_questions 
    context['is_exam_active'] = is_exam_active
    context['has_answered'] = has_answered
    context['start_exam_url'] = reverse('question_answer',args=[exam_pk, exam_questions.first().pk])
    return render(request, 'core/student_exam_detail.html', context)


def student_exam_list_view(request):
    context = {}
    from django.utils import timezone
    now = timezone.now()
    student_exams = StudentExamAccess.objects.filter(student=request.user)
    exams = [x.exam for x in student_exams]
    context['active_exams'] = [ex for ex in exams if ex.start_date<=now<=ex.end_date]
    context['passive_exams'] = [ex for ex in exams if ex.start_date>=now or now>=ex.end_date]
    return render(request, 'core/student_exam_list.html', context)

def delete_student_exam_access_view(request, exam_pk, student_pk):
    StudentExamAccess.objects.filter(exam__pk=exam_pk, student__pk=student_pk).delete()
    return HttpResponseRedirect(reverse_lazy('add_student_to_exam', args=[exam_pk,]))

def add_student_to_exam_view(request, exam_pk):
    context = {}
    exam = Exam.objects.get(pk=exam_pk)
    context['exam'] = exam
    context['exam_pk'] = exam_pk
    sea = StudentExamAccess.objects.filter(exam=exam)
    context['students'] = [x.student for x in sea]
    if request.method == 'GET':
        form = StudentExamAccessForm()
        context['form'] = form
    elif request.method == 'POST':
        form = StudentExamAccessForm(request.POST)
        
        if form.is_valid():
            student = form.cleaned_data['student']
            StudentExamAccess.objects.get_or_create(exam=exam, student=student)
            return HttpResponseRedirect(reverse_lazy('add_student_to_exam', args=[exam_pk]))

    return render(request, 'core/add_student_to_exam.html', context)


def question_detail_view(request, exam_pk, question_pk):

    context = {}
    context['exam_pk'] = exam_pk
    context['question_pk'] = question_pk
    question = get_object_or_404(Question, pk=question_pk)
    context['question'] = question
    try:
        context['question_choices'] = QuestionChoice.objects.filter(question=question_pk)
    except:
        print('#'*123)
    context['choice_form'] = QuestionChoiceForm() 
    
    if request.method == 'POST':
        form = QuestionChoiceForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            QuestionChoice.objects.create(
                question=Question.objects.get(pk=question_pk),
                **data
            )
    # try:
    return render(request, 'core/question_detail.html', context)
    # except:
    #     return HttpResponseRedirect(reverse_lazy('exam_detail', args=[exam_pk]))

def exam_create_view(request):
    context = {}

    if request.method == 'GET':
        form = ExamForm()
        context['form'] = form
    elif request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            Exam.objects.create(name=name, description=description)
    
    return render(request, 'core/exam_create.html', context)


def exam_list_view(request):
    # examleri database'den çekmem
    exams = Exam.objects.all()
    # daha sonrasında html'ı bununla renderlamak
    return render(request, 'core/exam_list.html', {'exams':exams})

class ExamDetailView(DetailView):
    model = Exam
    template_name = 'core/exam_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam_pk = self.kwargs.get('exam_pk')
        context['questions'] = Question.objects.filter(exam=exam_pk)
        context['exam_pk'] = exam_pk
        return context

    def get_object(self, queryset=None):
        return Exam.objects.get(pk=self.kwargs.get('exam_pk'))
        # return super().get_object(queryset=queryset)

def exam_detail_view(request, pk):
    exam = Exam.objects.get(pk=pk)
    context = {'exam':exam}
    return render(request, 'core/exam_detail.html', context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('homepage'))
        else:
            messages.error(request,'username or password not correct')
            return redirect(reverse('homepage'))
        
    else:
        form = AuthenticationForm()
    return render(request,'core/login.html', {'form':form})
