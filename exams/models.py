from django.db import models

# Create your models here.

class Exam(models.Model):
    exam_code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=600)
    full_points =  models.IntegerField()
    company_name = models.CharField(max_length=600, null=True, blank=True)
    academic_year = models.IntegerField(null=False, default=0)

    def __str__(self):
        return f"{self.name} - {self.exam_code}"
    
    class Meta:
        verbose_name_plural = "1. Exams"

class ExamDetails(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name='exam_details', null=False)
    title_order = models.IntegerField()
    title = models.CharField(max_length=600)
    details =  models.TextField()
    relation_to_question_no = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.title_order}. {self.title}"
    
    class Meta:
        verbose_name_plural = "2. Exam's Details"  
        ordering = ['exam__exam_code', 'title_order']    

class ExamQuestionAnswer(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name='exam_question_answer', null=False)
    question_serial = models.IntegerField()
    points = models.IntegerField()
    question =  models.TextField()
    sample_answer =  models.TextField()
    grading_guideline = models.TextField(null=True)

    def __str__(self):
        return f"{self.question_serial}. {self.question}"
    
    class Meta:
        verbose_name_plural = "3. Exam's Question Answer"  
        ordering = ['exam__exam_code', 'question_serial']    