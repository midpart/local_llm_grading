from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def index(request):
    error_message = ''
    try:
        error_message = ''

    except Exception as e:
        error_message = str(e)
    return render(request, 'llm_grading/index.html', {"error_message": error_message})
