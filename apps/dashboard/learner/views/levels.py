from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from apps.dashboard.learner.services.levels import can_learner_access_level, get_level_tasks_context
from core.decorators import role_required
from core.models import Level


@login_required
@role_required('learner')
def level_detail_view(request, level_id):
    level = get_object_or_404(
        Level,
        id=level_id,
        module__subject__classroom_subjects__classroom__students=request.user,
        module__subject__classroom_subjects__is_active=True,
        module__subject__is_active=True,
        module__is_active=True,
        is_active=True,
    )

    if not can_learner_access_level(request.user, level):
        raise Http404

    context = get_level_tasks_context(request.user, level)
    context['page_title'] = level.title

    return render(request, 'app/dashboard/learner/levels/page.html', context)
