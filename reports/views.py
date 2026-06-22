from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from llm_grading.common import *
from exams.models import *
from grading.models import *
import openpyxl
from django.utils import timezone
from django.http import HttpResponse
import re

@login_required(login_url='login')
def index(request):
    error_message = ''
    try:
        error_message = ''
    except Exception as e:
        error_message = str(e)
    return render(request, 'llm_grading/index.html', {"error_message": error_message})

@login_required(login_url='login')
def student_grade_report(request):
    template_name = 'llm_grading/student_grade_report.html'
    error_message = ""
    rows = []
    total_rows = 0
    page_obj = None
    exam_ids = []
    try:
        per_page = request.GET.get("per_page", settings.PER_PAGE)
        exam_ids = request.GET.getlist("exam_ids", None)
        exam_list = Exam.objects.all()
        rows = get_student_grade_report(exam_ids)
        paginator = Paginator(rows, per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        total_rows = paginator.count
    except Exception as e:
        error_message = e
    return render(request, template_name, {"page_obj": page_obj, "total_rows": total_rows, "error_message": error_message, 
                                           'exam_list' : exam_list, 'exam_ids': exam_ids})

def get_filter(request):
    filters = {
            "exam_ids":  request.GET.getlist("exam_ids", None),
        }
    return filters

@login_required(login_url='login')
def student_grade_report_xlx(request):
    # Get your filtered data
    exam_ids =  [x for x in request.GET.getlist("exam_ids") if x]#request.GET.getlist("exam_ids", None)
    exam_List = None
    if exam_ids is None or len(exam_ids) <= 0:
        exam_List = Exam.objects.all()
    else: 
        exam_List = Exam.objects.filter(id__in = exam_ids)
    

    # Create workbook
    file_name = f"Students_grade_report__{timezone.now().strftime("%Y-%m-%d-%H-%M-%S")}"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for exam in exam_List:
        exam_question_list = ExamQuestionAnswer.objects.filter(exam_id = exam.id).order_by('question_serial') 
        student_answer_list = StudentAnswer.objects.filter(exam_id = exam.id).order_by('student_name')
        student_answer_details_list = StudentAnswerDetails.objects.filter(exam_id = exam.id)
        student_answer_grade_list = StudentGrade.objects.filter(exam_id = exam.id)

        sheet_name  = f"{exam.name}-{exam.academic_year}"
        sheet_name = re.sub(r'[:\\/*?\[\]]', '_', sheet_name)
        sheet_name = sheet_name[:31]
        ws = wb.create_sheet(title=sheet_name)
        header_array = ["exam_id","exam_name","academic_year","full_points", "exam_code", "company_name"]
        for question in exam_question_list:
            header_array.append(f"Q-{question.question_serial}_point")
            header_array.append(f"Q-{question.question_serial}_question")
            header_array.append(f"Q-{question.question_serial}_sample_answer")
        header_array.extend(["student_name", "total_point", "grade", "llm_model" ])
        for question in exam_question_list:
            header_array.append(f"Q-{question.question_serial}_stu_answer")
            header_array.append(f"Q-{question.question_serial}_llm_has_response")
            header_array.append(f"Q-{question.question_serial}_llm_score_points")
            header_array.append(f"Q-{question.question_serial}_llm_score_details")
            header_array.append(f"Q-{question.question_serial}_llm_used_alternative_approach")
            header_array.append(f"Q-{question.question_serial}_llm_feedback")
            header_array.append(f"Q-{question.question_serial}_llm_response_in_sec")
            header_array.append(f"Q-{question.question_serial}_llm_response_in_min")
            header_array.append(f"Q-{question.question_serial}_llm_input_token")
            header_array.append(f"Q-{question.question_serial}_llm_output_tokens")
            header_array.append(f"Q-{question.question_serial}_llm_total_tokens")
            header_array.append(f"Q-{question.question_serial}_llm_response_total_duration_sec")
            header_array.append(f"Q-{question.question_serial}_llm_response_prompt_eval_duration_sec")
            header_array.append(f"Q-{question.question_serial}_llm_response_eval_duration_sec")
            header_array.append(f"Q-{question.question_serial}_llm_fix_score_points")
            header_array.append(f"Q-{question.question_serial}_llm_fix_rubric_status")
            header_array.append(f"Q-{question.question_serial}_llm_fix_rubric_points")
            header_array.append(f"Q-{question.question_serial}_llm_score_points")
        ws.append(header_array) 

        # Add data
        exam_data_rows = [exam.id, exam.name, exam.academic_year, exam.full_points, exam.exam_code, exam.company_name]
        for question in exam_question_list:
            exam_data_rows.append(question.points)
            exam_data_rows.append(question.question)
            exam_data_rows.append(question.sample_answer)
            
        student_names = sorted(set(student_answer_list.values_list('student_name', flat=True)))

        for student_name in student_names:
            data_rows = []
            print(f"student_name: {student_name}")
            temp_answer_list = student_answer_list.filter(student_name = student_name)
            temp_grade = student_answer_grade_list.filter(student_name = student_name).first()

            data_rows.extend(exam_data_rows)
            data_rows.append(student_name)
            if temp_grade is None:
                data_rows.extend([None, None, None])
            else: 
                llm_model = None
                if temp_answer_list is not None:
                    llm_model = temp_answer_list.first().llm_model
                data_rows.extend([temp_grade.total_point, temp_grade.grade, llm_model])
            for question in exam_question_list:
                temp_answer = None
                if temp_answer_list is not None:
                    temp_answer = temp_answer_list.filter(question_serial = question.question_serial).first()
                if temp_answer is None:
                    data_rows.extend([None, get_true_false(False), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None])
                else:
                    details = ""
                    temp_details = student_answer_details_list.filter(student_answer_id = temp_answer.id)
                    if temp_details is not None:
                        for temp_detail in temp_details:
                            details += f"title: {temp_detail.title}, score: {temp_detail.score}, max_score: {temp_detail.max_score}, is_from_guideline: {get_true_false(temp_detail.is_from_guideline)} \n"
                    data_rows.extend([temp_answer.answer, get_true_false(temp_answer.llm_has_response), temp_answer.llm_score_points,
                                          details, get_true_false(temp_answer.llm_used_alternative_approach), temp_answer.llm_feedback, 
                                          temp_answer.llm_response_in_sec, temp_answer.llm_response_in_sec / 60, temp_answer.llm_input_token, 
                                          temp_answer.llm_output_tokens, (temp_answer.llm_input_token + temp_answer.llm_output_tokens), 
                                          temp_answer.llm_response_total_duration_sec, temp_answer.llm_response_prompt_eval_duration_sec, 
                                          temp_answer.llm_response_eval_duration_sec, get_true_false(temp_answer.llm_fix_score_points)
                                          , get_true_false(temp_answer.llm_fix_rubric_status), get_true_false(temp_answer.llm_fix_rubric_points)
                                          , get_true_false(temp_answer.llm_score_points)])
            
            print(f"Total Colum: {len(data_rows)}")
            ws.append(data_rows)

    # Prepare response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{file_name}.xlsx"'

    wb.save(response)
    return response