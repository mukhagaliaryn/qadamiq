from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from apps.dashboard.learner.services.levels import can_learner_access_level, can_learner_access_task
from apps.dashboard.learner.services.tasks import check_test_task_answers, get_test_task_context, \
    check_matching_task_answers, get_matching_task_context, get_matching_saved_result, get_test_saved_result, \
    check_ordering_task_answers, get_ordering_task_context, get_ordering_saved_result, save_audio_submission, \
    complete_audio_task, get_audio_saved_result, get_audio_task_context
from core.decorators import role_required
from core.models import Task



@login_required
@role_required('learner')
def task_detail_view(request, task_id):
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

    if task.task_type == Task.TaskType.TEST:
        return handle_test_task(request, task)

    if task.task_type == Task.TaskType.MATCHING:
        return handle_matching_task(request, task)

    if task.task_type == Task.TaskType.ORDERING:
        return handle_ordering_task(request, task)

    if task.task_type == Task.TaskType.AUDIO:
        return handle_audio_task(request, task)

    return render(request, 'app/dashboard/learner/tasks/unsupported.html', {
        'page_title': task.title,
        'task': task,
    })


# Test views
# ----------------------------------------------------------------------------------------------------------------------
def handle_test_task(request, task):
    result = None
    if request.method == 'POST':
        result = check_test_task_answers(request.user, task, request.POST)

        if result['is_correct']:
            messages.success(request, 'Задание выполнено успешно.')
        else:
            messages.error(request, 'Есть ошибки. Попробуйте ещё раз.')

    else:
        result = get_test_saved_result(request.user, task)

    context = get_test_task_context(request.user, task)
    context['page_title'] = task.title
    context['result'] = result
    context['is_completed_now'] = bool(result and result['is_correct'])
    context['is_saved_result'] = bool(result and result.get('is_saved_result'))

    return render(request, 'app/dashboard/learner/tasks/test.html', context)


# Matching views
# ----------------------------------------------------------------------------------------------------------------------
def handle_matching_task(request, task):
    result = None

    if request.method == 'POST':
        result = check_matching_task_answers(request.user, task, request.POST)

        if result['is_correct']:
            messages.success(request, 'Задание выполнено успешно.')
        else:
            messages.error(request, 'Есть ошибки. Попробуйте ещё раз.')

    else:
        result = get_matching_saved_result(request.user, task)

    context = get_matching_task_context(request.user, task)
    context['page_title'] = task.title
    context['result'] = result
    context['is_completed_now'] = bool(result and result['is_correct'])
    context['has_errors_now'] = bool(result and not result['is_correct'])
    return render(request, 'app/dashboard/learner/tasks/matching.html', context)


# Ordering views
# ----------------------------------------------------------------------------------------------------------------------
def handle_ordering_task(request, task):
    result = None
    if request.method == 'POST':
        result = check_ordering_task_answers(request.user, task, request.POST)
        if result['is_correct']:
            messages.success(request, 'Задание выполнено успешно.')
        else:
            messages.error(request, 'Есть ошибки. Попробуйте ещё раз.')

    else:
        result = get_ordering_saved_result(request.user, task)

    context = get_ordering_task_context(request.user, task)
    context['page_title'] = task.title
    context['result'] = result
    context['is_completed_now'] = bool(result and result['is_correct'])
    context['is_saved_result'] = bool(result and result.get('is_saved_result'))
    return render(request, 'app/dashboard/learner/tasks/ordering.html', context)


# Audio view
# ----------------------------------------------------------------------------------------------------------------------
def handle_audio_task(request, task):
    result = None
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'upload_audio':
            audio_file = request.FILES.get('audio_file')

            if not audio_file:
                messages.error(request, 'Аудиофайл не найден.')
            else:
                save_audio_submission(request.user, task, audio_file)
                messages.success(request, 'Аудиозапись сохранена. Заполните чек-лист.')

        elif form_type == 'checklist':
            checklist_data = {
                'sound_clear': request.POST.get('sound_clear'),
                'steps_ordered': request.POST.get('steps_ordered'),
                'file_saved': request.POST.get('file_saved'),
            }
            if all(checklist_data.values()):
                complete_audio_task(request.user, task, checklist_data)
                result = get_audio_saved_result(request.user, task)
                messages.success(request, 'Задание выполнено успешно.')
            else:
                messages.error(request, 'Ответьте на все вопросы чек-листа.')
    else:
        result = get_audio_saved_result(request.user, task)

    context = get_audio_task_context(request.user, task)
    context['page_title'] = task.title
    context['result'] = result
    context['is_completed_now'] = bool(result and result.get('is_correct'))
    context['is_saved_result'] = bool(result and result.get('is_saved_result'))

    return render(request, 'app/dashboard/learner/tasks/audio.html', context)
