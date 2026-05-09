from django.contrib import admin

# Register your models here.
from .models import StudentAnswer, StudentGrade

admin.site.register(StudentAnswer)
admin.site.register(StudentGrade)