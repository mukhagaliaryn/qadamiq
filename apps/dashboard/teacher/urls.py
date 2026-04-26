from django.urls import path
from apps.dashboard.teacher import views

app_name = 'teacher'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('classrooms/', views.classrooms_view, name='classrooms'),
    path('classrooms/create/', views.classroom_create_view, name='classroom-create'),
    path('classrooms/<int:classroom_id>/edit/', views.classroom_update_view, name='classroom-update'),
    path('classrooms/<int:classroom_id>/delete/', views.classroom_delete_view, name='classroom-delete'),

    path('classrooms/assign-subject/', views.classroom_subject_assign_view, name='classroom-subject-assign'),
    path('classrooms/attach-students/', views.classroom_students_attach_view, name='classroom-students-attach'),
    path('classrooms/<int:classroom_id>/students/<int:student_id>/remove/', views.classroom_student_remove_view, name='classroom-student-remove'),

    path('students/', views.students_view, name='students'),
]
