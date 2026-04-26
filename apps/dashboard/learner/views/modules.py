from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from apps.dashboard.learner.services.modules import get_module_levels_context, get_modules_page_context
from core.decorators import role_required
from core.models import Module


@login_required
@role_required('learner')
def modules_view(request):
    context = get_modules_page_context(request.user)
    return render(request, 'app/dashboard/learner/modules/list.html', context)


@login_required
@role_required('learner')
def module_detail_view(request, module_id):
    module = get_object_or_404(
        Module,
        id=module_id,
        subject__classroom_subjects__classroom__students=request.user,
        subject__classroom_subjects__is_active=True,
        subject__is_active=True,
        is_active=True,
    )
    context = get_module_levels_context(request.user, module)
    context['page_title'] = module.title
    return render(request, 'app/dashboard/learner/modules/page.html', context)