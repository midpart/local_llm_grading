from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Exam, ExamDetails, ExamQuestionAnswer

#admin.site.register(Exam)
@admin.register(Exam)
class SystemSettings(admin.ModelAdmin):
    list_display = ('id', 'exam_code', 'name', 'full_points', 'company_name', 'academic_year')  
    #list_per_page = settings.PER_PAGE
    
#admin.site.register(ExamDetails)
@admin.register(ExamDetails)
class SystemSettings(admin.ModelAdmin):
    list_display = ('id', 'exam__name', 'title_order', 'title', 'relation_to_question_no')  
    list_filter = ('exam__name',)

#admin.site.register(ExamQuestionAnswer)
@admin.register(ExamQuestionAnswer)
class SystemSettings(admin.ModelAdmin):
    list_display = ('id', 'exam__name', 'question_serial', 'points', 'rubric_titles')  
    list_filter = ('exam__name', 'question_serial',)