from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from llm_grading.common import *
import pandas as pd
from django.db import transaction
from exams.models import *
from grading.models import *
from grading.examDto import *
from django.contrib.auth.decorators import login_required
import time
import re
import json
# Create your views here.

@login_required(login_url='login')
def upload_student_answers(request):
    template_name = 'llm_grading/upload_student_answers.html'
    exams = Exam.objects.all()
    llm_models = get_all_ollama_llm_model()

    return render(request, template_name, {'exams' : exams, 'llm_models': llm_models})

def get_exam_question_dto(exam_obj, exam_details, exam_questions):

    dto_list = []
    for exam_question in exam_questions:
        temp_dto = ExamQuestionDTO(
            question_serial = exam_question.question_serial,
            points = exam_question.points,
            question = exam_question.question,
            sample_answer = exam_question.sample_answer,
            details = []
        )
        for exam_detail in exam_details:
            if exam_detail.relation_to_question_no is None or pd.isna(exam_detail.relation_to_question_no):
                continue
            temp_array = [int(x.strip()) for x in exam_detail.relation_to_question_no.split(",") if x.strip() and x.strip().lower() != "nan"]
            if temp_dto.question_serial in temp_array:
                temp_dto.details.append(ExamDetailsDTO(title=exam_detail.title, details=exam_detail.details, relation_to_question_no=exam_detail.relation_to_question_no))
        
        dto_list.append(temp_dto)

    return dto_list

def get_exam_details_context(examQuestionDto, student_answer):
    context = ""
    if examQuestionDto is not None:
        context = f"""
You are a STRICT grading engine.

You do NOT behave like a chatbot.
You ONLY output structured JSON.
        """
        if len(examQuestionDto.details) > 0:
            context += f"""
CONTEXT (use internally only):
            """
        for detail in examQuestionDto.details:
             context += f"""
{detail.title.upper()}
{detail.details}

            """
        context += f"""
QUESTION:
{examQuestionDto.question}
        
REFERENCE ANSWER (internal use only):
{examQuestionDto.sample_answer}

STUDENT ANSWER:
{student_answer}

-----------------------
SCORING RULES (MUST FOLLOW EXACTLY)

1. question_point = {examQuestionDto.points} (fixed)
2. student_point must be between 0 and {examQuestionDto.points}
3. bonus_points = 0 (always)
4. feedback = max 3 short bullet-style strings
5. Be consistent and objective. Do NOT be lenient or strict randomly.
6. Base scoring ONLY on rubric quality, not writing style.

-----------------------
RUBRIC (DETERMINISTIC)

UNDERSTANDING (0–40% of score)
APPLICATION (0–40% of score)
CRITICAL THINKING (0–20% of score)

Convert rubric result into final student_point.

-----------------------
OUTPUT FORMAT (STRICT JSON ONLY)

{{
  "question_point": {examQuestionDto.points},
  "student_point": number,
  "bonus_points": 0,
  "feedback": "",
}}

No explanation. No markdown. No extra text.
Start with {{ and end with }}.
            """
             
    return context

def request_llm(prompt, llm_model):

    response = ollama.chat(
        model=llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a deterministic grading engine. "
                    "You must follow scoring rules exactly. "
                    "Return ONLY valid JSON. No exceptions."
                )
            },
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0.0,
            "top_p": 1.0,
            "repeat_penalty": 1.0,
            "num_predict": 350
        }
    )
    return response["message"]["content"].strip()

def parse_json_safe(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None
    except:
        return None

def get_grade(total):
    grade = None
    if 90 <= total <= 100:
        grade = 12
    elif 75 <= total <= 89:
        grade = 10
    elif 65 <= total <= 74:
        grade = 7
    elif 55 <= total <= 64:
        grade = 4
    elif 40 <= total <= 54:
        grade = 2
    elif 0 <= total <= 39:
        grade = 0
    
    return grade

@csrf_exempt
def process_student_answer_files(request):
    if request.method == "POST" and request.FILES.getlist("excel_files"):
        excel_files = request.FILES.getlist("excel_files")
        exam_id = request.POST.get("exam_id")
        llm_model = request.POST.get("llm_model")
        message = ""
        success = False
        fileName = ""
        try:
            for excel_file in excel_files:
                check_file(excel_file)
            exam_obj = Exam.objects.get(pk=exam_id)
            llm_models = get_all_ollama_llm_model()
            if exam_obj is None:
                raise ValueError (f"Unable to find exam with id : {exam_id}")
            if llm_model not in llm_models:
                raise ValueError(f"{llm_model} is not in the Ollama model lists")
            
            all_db_student_answer = StudentAnswer.objects.filter(exam_id = exam_id)
            all_db_student_grade = StudentGrade.objects.filter(exam__id = exam_id)
            exam_details = ExamDetails.objects.filter(exam__id = exam_id)
            exam_questions = ExamQuestionAnswer.objects.filter(exam__id = exam_id)
            exam_detail_dto = get_exam_question_dto(exam_obj, exam_details, exam_questions)

            for excel_file in excel_files:
                add_student_answer_db_list = []
                update_student_answer_db_list = []

                add_student_grade_db_list = []
                update_student_grade_db_list = []

                df_file = pd.read_excel(excel_file, sheet_name=0)
                temp_file_name = excel_file.name
                fileName = temp_file_name
                temp_studentGrade = all_db_student_grade.filter(student_name=temp_file_name).first() if all_db_student_grade is not None else None
                if temp_studentGrade is None:
                    temp_studentGrade = StudentGrade(
                        exam = exam_obj,
                        student_name = temp_file_name,
                    )
                    add_student_grade_db_list.append(temp_studentGrade)
                else:
                    update_student_grade_db_list.append(temp_studentGrade)

                for index, row in df_file.iterrows(): 
                    question_serial = row["question_serials"]
                    answer = row["answer"]
                    temp_studentAnswer = all_db_student_answer.filter(student_name=temp_file_name, question_serial=question_serial).first() if all_db_student_answer is not None else None
                    if temp_studentAnswer is None:
                        temp_studentAnswer = StudentAnswer(
                            exam = exam_obj,
                            student_name = temp_file_name,
                            question_serial = question_serial
                        )
                        add_student_answer_db_list.append(temp_studentAnswer)
                    else: 
                        update_student_answer_db_list.append(temp_studentAnswer)
                    temp_studentAnswer.answer = answer

                    temp_exam_question_details = next( (temp_details for temp_details in exam_detail_dto if temp_details.question_serial == temp_studentAnswer.question_serial),None)
                    if temp_exam_question_details is None:
                        continue

                    temp_context = get_exam_details_context(temp_exam_question_details, temp_studentAnswer.answer)
                    temp_studentAnswer.llm_model = llm_model

                    start_time = time.time()
                    temp_llm_result = request_llm(temp_context, temp_studentAnswer.llm_model)
                    end_time = time.time()
                    elapsed = end_time - start_time
                    temp_data = parse_json_safe(temp_llm_result)

                    temp_studentAnswer.llm_start_time = start_time
                    temp_studentAnswer.llm_end_time = end_time
                    temp_studentAnswer.llm_response_in_sec = elapsed
                    temp_studentAnswer.llm_response_raw = temp_llm_result

                    if not temp_data:
                        temp_studentAnswer.llm_has_response = False
                        continue
                
                    temp_studentAnswer.llm_feedback = temp_data.get("feedback", "")
                    temp_studentAnswer.llm_score_points = temp_data.get("student_point", 0)
                    temp_studentAnswer.llm_has_response = True
                    if temp_studentGrade.total_point is None:
                        temp_studentGrade.total_point = 0
                    temp_studentGrade.total_point +=temp_studentAnswer.llm_score_points
            
                if temp_studentGrade.total_point is not None:
                    temp_studentGrade.grade = get_grade(temp_studentGrade.total_point)

                with transaction.atomic():
                    if len(add_student_grade_db_list) > 0:
                        StudentGrade.objects.bulk_create(add_student_grade_db_list, batch_size=100)
                    if len(update_student_grade_db_list) > 0:
                        StudentGrade.objects.bulk_update(update_student_grade_db_list, ["total_point"
                                                                , "grade"
                                                                ], batch_size=100)

                    if len(add_student_answer_db_list) > 0:
                        StudentAnswer.objects.bulk_create(add_student_answer_db_list, batch_size=100)
                    if len(update_student_answer_db_list) > 0:
                        StudentAnswer.objects.bulk_update(update_student_answer_db_list, ["answer"
                                                                , "llm_score_points"
                                                                , "llm_model"
                                                                , "llm_feedback"
                                                                , "llm_start_time"
                                                                , "llm_end_time"
                                                                , "llm_response_in_sec"
                                                                , "llm_response_raw"
                                                                , "llm_has_response"
                                                                ], batch_size=100)
            
            message = "Operation is successful."
            success = True
        except Exception as e:
            message = f"Error reading sheet {fileName}: {e}"
    return JsonResponse({"success": success, "message": message})    