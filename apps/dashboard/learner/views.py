from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.decorators import role_required


@login_required
@role_required('learner')
def dashboard_view(request):
    return render(request, 'app/dashboard/learner/page.html', {
        'page_title': 'Панель ученика',
    })


@login_required
@role_required('learner')
def modules_view(request):
    return render(request, 'app/dashboard/learner/modules/page.html', {
        'page_title': 'Модули',
    })


@login_required
@role_required('learner')
def progress_view(request):
    return render(request, 'app/dashboard/learner/progress/page.html', {
        'page_title': 'Прогресс',
    })
