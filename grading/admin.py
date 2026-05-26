from django.contrib import admin

# Register your models here.
from .models import StudentAnswer, StudentGrade, StudentAnswerDetails

# admin.site.register(StudentAnswer)
# admin.site.register(StudentGrade)

@admin.register(StudentGrade)
class SystemSettings(admin.ModelAdmin):
    list_display = ('id', 'exam__name', 'student_name', 'total_point', 'grade')  
    #list_per_page = settings.PER_PAGE

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(StudentAnswer)
class SystemSettings(admin.ModelAdmin):
    list_display = ('id', 'exam__name', 'student_name', 'question_serial', 'llm_model', 'llm_score_points', 'llm_used_alternative_approach', 'llm_has_response', 'llm_response_in_sec')  
    #list_per_page = settings.PER_PAGE

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False 


@admin.register(StudentAnswerDetails)
class SystemSettings(admin.ModelAdmin):
    list_display = ('id', 'exam__name', 'student_answer__student_name', 'student_answer__question_serial', 'title', 'score', 'max_score', 'is_from_guideline')  
    #list_per_page = settings.PER_PAGE

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False    