from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.decorators import role_required


@login_required
@role_required('teacher')
def dashboard_view(request):
    return render(request, 'app/dashboard/teacher/page.html', {
        'page_title': 'Панель учителя',
    })


@login_required
@role_required('teacher')
def classrooms_view(request):
    return render(request, 'app/dashboard/teacher/classrooms/page.html', {
        'page_title': 'Классы',
    })


@login_required
@role_required('teacher')
def students_view(request):
    return render(request, 'app/dashboard/teacher/students/page.html', {
        'page_title': 'Ученики',
    })
