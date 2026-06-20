from django.db import models
from exams.models import Exam

# Create your models here.
class StudentAnswer(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name='student_answer', null=False)
    student_name = models.CharField(max_length=255)
    question_serial =  models.IntegerField()
    answer =  models.TextField()

    llm_score_points =  models.FloatField(null=True)
    llm_used_alternative_approach = models.BooleanField(null=True)
    llm_model = models.CharField(max_length=600, null=True, blank=True)
    llm_feedback =  models.TextField(null=True)
    llm_start_time = models.FloatField(null=True)
    llm_end_time = models.FloatField(null=True)
    llm_response_in_sec = models.FloatField(null=True)
    llm_response_raw =  models.TextField(null=True)
    llm_has_response =  models.BooleanField(null=True)
    llm_input_token = models.IntegerField(null=True)
    llm_output_tokens = models.IntegerField(null=True)
    llm_response_total_duration_sec = models.FloatField(null=True)
    llm_response_prompt_eval_duration_sec = models.FloatField(null=True)
    llm_response_eval_duration_sec = models.FloatField(null=True)
    llm_context_raw =  models.TextField(null=True)
    llm_fix_score_points =  models.BooleanField(null=True)
    llm_fix_rubric_status =  models.BooleanField(null=True)
    llm_fix_rubric_points =  models.BooleanField(null=True)

    def __str__(self):
        return f"{self.student_name} - {self.question_serial}"
    
    class Meta:
        verbose_name_plural = "1. StudentAnswers"

class StudentAnswerDetails(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name='student_answer_details_exam', null=False)
    student_answer = models.ForeignKey(StudentAnswer, on_delete=models.RESTRICT, related_name='student_answer_details_answer', null=False)

    title = models.CharField(max_length=600)
    score = models.FloatField(null=False)
    max_score = models.FloatField(null=False)
    is_from_guideline = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.score}"
    
    class Meta:
        verbose_name_plural = "2. StudentAnswerDetails"

class StudentGrade(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name='student_grade', null=False)
    student_name = models.CharField(max_length=255)
    total_point =  models.FloatField(null=True)
    grade =  models.IntegerField(null=True)

    def __str__(self):
        return f"{self.student_name} - {self.grade}"
    
    class Meta:
        verbose_name_plural = "3. StudentGrade"


class LlmLog(models.Model):
    student_name = models.CharField(max_length=255)
    exam_id = models.IntegerField()
    question_serial =  models.IntegerField()
    creation_date_time = models.DateTimeField(auto_now_add=True)

    llm_model = models.CharField(max_length=600, null=True, blank=True)
    llm_feedback =  models.TextField(null=True)
    llm_start_time = models.FloatField(null=True)
    llm_end_time = models.FloatField(null=True)
    llm_response_in_sec = models.FloatField(null=True)
    llm_response_raw =  models.TextField(null=True)
    llm_input_token = models.IntegerField(null=True)
    llm_output_tokens = models.IntegerField(null=True)
    llm_response_total_duration_sec = models.FloatField(null=True)
    llm_response_prompt_eval_duration_sec = models.FloatField(null=True)
    llm_response_eval_duration_sec = models.FloatField(null=True)
    llm_context_raw =  models.TextField(null=True)
    llm_fix_score_points =  models.BooleanField(null=True)
    llm_fix_rubric_status =  models.BooleanField(null=True)
    llm_fix_rubric_points =  models.BooleanField(null=True)
    llm_score_points =  models.FloatField(null=True)

    def __str__(self):
        return f"{self.llm_model} - {self.question_serial}"
    
    class Meta:
        verbose_name_plural = "4. LlmLogs"