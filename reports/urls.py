from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('student_grade_report/', views.student_grade_report, name='studentGradeReport'),

    path('login/', auth_views.LoginView.as_view(template_name='llm_grading/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]