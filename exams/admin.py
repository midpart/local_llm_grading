from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Exam, ExamDetails, ExamQuestionAnswer

admin.site.register(Exam)
admin.site.register(ExamDetails)
admin.site.register(ExamQuestionAnswer)