from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from llm_grading.common import *

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
    try:
        per_page = request.GET.get("per_page", settings.PER_PAGE)
        
        rows = get_student_grade_report()
        paginator = Paginator(rows, per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        total_rows = paginator.count
    except Exception as e:
        error_message = e
    return render(request, template_name, {"page_obj": page_obj, "total_rows": total_rows, "error_message": error_message})
