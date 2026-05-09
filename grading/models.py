from django.db import models
from exams.models import Exam

# Create your models here.
class StudentAnswer(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name='student_answer', null=False)
    student_name = models.CharField(max_length=255)
    question_serial =  models.IntegerField()
    answer =  models.TextField()

    llm_score_points =  models.FloatField(null=True)
    llm_model = models.CharField(max_length=600, null=True, blank=True)
    llm_feedback =  models.TextField(null=True)
    llm_start_time = models.FloatField(null=True)
    llm_end_time = models.FloatField(null=True)
    llm_response_in_sec = models.FloatField(null=True)
    llm_response_raw =  models.TextField(null=True)

    def __str__(self):
        return f"{self.student_name} - {self.question_serial}"
    
    class Meta:
        verbose_name_plural = "1. StudentAnswers"

class StudentGrade(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name='student_grade', null=False)
    student_name = models.CharField(max_length=255)
    total_point =  models.FloatField()
    grade =  models.IntegerField()

    def __str__(self):
        return f"{self.student_name} - {self.grade}"
    
    class Meta:
        verbose_name_plural = "2. StudentGrade"