from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "exams"

urlpatterns = [
    path('upload_exam/', views.upload_exam, name='uploadExam'),
    path('process_exam_file/', views.process_exam_file, name='processExamFile'),
]