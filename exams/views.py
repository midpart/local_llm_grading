from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from llm_grading.common import *
import pandas as pd
from django.db import transaction
from exams.models import *
from django.contrib.auth.decorators import login_required
from llm_grading.forms import *
# Create your views here.

@login_required(login_url='login')
def upload_exam(request):
    template_name = 'llm_grading/upload_exam.html'
    form = UploadFileForm()

    return render(request, template_name, {'form': form})

@csrf_exempt
def process_exam_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        excel_file = request.FILES["file"]
        message = ""
        success = False
        try:
            check_file(excel_file)
            pd_file = pd.ExcelFile(excel_file)

            overview_sheetName = "overview"
            description_sheetName = "description"
            question_sample_answer_sheetName = "question_sample_answer"

            sheet_names = pd_file.sheet_names
            name_array = [overview_sheetName, description_sheetName, question_sample_answer_sheetName]
            missing_sheets = [
                sheet for sheet in name_array
                if sheet not in sheet_names
            ]
            if missing_sheets:
                raise ValueError(
                    f"Missing sheets: {', '.join(missing_sheets)}"
                )

            df_overview = pd.read_excel(excel_file, sheet_name=overview_sheetName).iloc[0]
            df_description = pd.read_excel(excel_file, sheet_name=description_sheetName)
            df_questions = pd.read_excel(excel_file, sheet_name=question_sample_answer_sheetName)
            
            temp_exam_code=df_overview["exam_code"]
            temp_name=df_overview["exam_name"]
            temp_full_points=df_overview["full_points"]
            temp_company_name=df_overview["company"]
            temp_academic_year=df_overview["academic_year"]

            temp_exam = Exam.objects.filter(exam_code=temp_exam_code).first()
            
            add_detail_db_list = []
            update_detail_db_list = []
            remove_detail_db_list = []

            add_question_db_list = []
            update_question_db_list = []
            remove_question_db_list = []

            detail_db_list = None
            question_db_list = None
            if temp_exam is None:
                temp_exam = Exam (exam_code=temp_exam_code)
            else:
                detail_db_list = ExamDetails.objects.filter(exam__id=temp_exam.id)
                question_db_list = ExamQuestionAnswer.objects.filter(exam__id=temp_exam.id)
            temp_exam.name = temp_name
            temp_exam.full_points = temp_full_points
            temp_exam.company_name = temp_company_name
            temp_exam.academic_year = temp_academic_year

            details_list = []
            for index, row in df_description.iterrows():
                temp_title = row["Title"]
                
                temp_examdetails = detail_db_list.filter(title=temp_title).first() if detail_db_list is not None else None
                is_new_details = False
                if temp_examdetails is None:
                    temp_examdetails = ExamDetails (
                        exam = temp_exam,
                        title = temp_title,
                    )
                    is_new_details = True
                temp_examdetails.title_order = index + 1
                temp_examdetails.details = row["Details"]
                temp_examdetails.relation_to_question_no = row["relation_to_question_no"]

                if is_new_details:
                    add_detail_db_list.append(temp_examdetails)
                else: 
                    update_detail_db_list.append(temp_examdetails)

                details_list.append(temp_title)
            remove_detail_db_list = detail_db_list.exclude(title__in=details_list) if detail_db_list is not None else []

            serial_list = []
            for index, row in df_questions.iterrows():
                temp_serial = row["serial"]
                
                temp_question = question_db_list.filter(question_serial=temp_serial).first() if question_db_list is not None else None
                is_new_question = False
                if temp_question is None:
                    temp_question = ExamQuestionAnswer (
                        exam = temp_exam,
                        question_serial = temp_serial,
                    )
                    is_new_question = True
                temp_question.points = row["points"]
                temp_question.question = row["question"]
                temp_question.sample_answer = row["sample_answer"]
                temp_question.grading_guideline = row["grading_guideline"]
                temp_question.rubric_titles = "" 
                if "rubric_titles" in df_questions.columns:
                    rubric_titles = row["rubric_titles"]
                    if rubric_titles is not None and len(rubric_titles) > 0:
                        temp_question.rubric_titles = ",".join(item.strip().lower() for item in rubric_titles.split(","))

                if is_new_question:
                    add_question_db_list.append(temp_question)
                else: 
                    update_question_db_list.append(temp_question)

                serial_list.append(temp_serial)
            remove_question_db_list = question_db_list.exclude(question_serial__in=serial_list) if question_db_list is not None else []

            filename = excel_file.name
            with transaction.atomic():
                temp_exam.save()

                if len(add_detail_db_list) > 0:
                    ExamDetails.objects.bulk_create(add_detail_db_list, batch_size=100)
                if len(update_detail_db_list) > 0:
                    ExamDetails.objects.bulk_update(update_detail_db_list, ["title_order"
                                                          , "details"
                                                          , "relation_to_question_no"
                                                          ], batch_size=100)
                if len(remove_detail_db_list) > 0:
                    remove_detail_db_list.delete()

                if len(add_question_db_list) > 0:
                    ExamQuestionAnswer.objects.bulk_create(add_question_db_list, batch_size=100)
                if len(update_question_db_list) > 0:
                    ExamQuestionAnswer.objects.bulk_update(update_question_db_list, ["points"
                                                          , "question"
                                                          , "sample_answer"
                                                          , "grading_guideline"
                                                          , "rubric_titles"
                                                          ], batch_size=100)
                if len(remove_question_db_list) > 0:
                    remove_question_db_list.delete()
            
            message = "Operation is successful."
            success = True
        except Exception as e:
            message = f"Error reading sheet: {e}"
            #return JsonResponse({"success": False, "error": f"Error reading sheet: {e}"})
    return JsonResponse({"success": success, "message": message})    