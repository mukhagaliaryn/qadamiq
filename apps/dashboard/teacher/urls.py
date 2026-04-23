from django.urls import path
from .views import teacher_dashboard_view

app_name = 'teacher'

urlpatterns = [
    path('', teacher_dashboard_view, name='dashboard'),
]