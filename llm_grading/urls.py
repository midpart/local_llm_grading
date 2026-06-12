from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('grading/', include('grading.urls')),
    path('', include('reports.urls')),
    path('exams/', include('exams.urls')),
]
