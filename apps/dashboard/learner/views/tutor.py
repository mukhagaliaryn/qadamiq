import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from apps.dashboard.learner.services.levels import (
    can_learner_access_level,
    can_learner_access_task,
)
from apps.dashboard.learner.services.tutor import (
    TutorError,
    get_conversation_payload,
    get_or_create_conversation,
    send_message,
)
from core.decorators import role_required
from core.models import Task


def _get_accessible_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        level__module__subject__classroom_subjects__classroom__students=request.user,
        level__module__subject__classroom_subjects__is_active=True,
        level__module__subject__is_active=True,
        level__module__is_active=True,
        level__is_active=True,
        is_active=True,
    )

    if not can_learner_access_level(request.user, task.level):
        raise Http404

    if not can_learner_access_task(request.user, task):
        raise Http404

    return task


@login_required
@role_required('learner')
@require_http_methods(['GET', 'POST'])
def tutor_view(request, task_id):
    task = _get_accessible_task(request, task_id)

    if request.method == 'GET':
        conversation = get_or_create_conversation(request.user, task)
        return JsonResponse({
            'ok': True,
            'messages': get_conversation_payload(conversation),
        })

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        payload = {}

    user_text = payload.get('message', '')

    try:
        result = send_message(request.user, task, user_text)
    except TutorError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=200)

    return JsonResponse({
        'ok': True,
        'reply': result['reply'],
        'state': result['state'],
    })
