from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "grading"

urlpatterns = [
    path('upload_student_answers/', views.upload_student_answers, name='uploadStudentAnswers'),
    path('process_student_answer_files/', views.process_student_answer_files, name='processStudentAnswers'),
]