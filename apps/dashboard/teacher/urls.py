from django.urls import path
from apps.dashboard.teacher import views

app_name = 'teacher'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('classrooms/', views.classrooms_view, name='classrooms'),
    path('students/', views.students_view, name='students'),
]