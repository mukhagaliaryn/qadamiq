from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.dashboard.learner.services.dashboard import get_learner_dashboard_context
from core.decorators import role_required


@login_required
@role_required('learner')
def dashboard_view(request):
    context = get_learner_dashboard_context(request.user)

    return render(request, 'app/dashboard/learner/page.html', context)


@login_required
@role_required('learner')
def progress_view(request):
    context = get_learner_dashboard_context(request.user)
    context['page_title'] = 'Прогресс'

    return render(request, 'app/dashboard/learner/progress/page.html', context)
