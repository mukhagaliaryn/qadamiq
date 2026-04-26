from core.models import Task, TaskProgress

from .modules import get_module_levels_context


def can_learner_access_level(learner, level):
    context = get_module_levels_context(learner, level.module)

    for item in context['level_items']:
        if item['level'].id == level.id:
            return not item['is_locked']

    return False


def get_level_tasks(level):
    return Task.objects.filter(
        level=level,
        is_active=True,
    ).order_by('order', 'id')


def is_task_completed(learner, task):
    return TaskProgress.objects.filter(
        learner=learner,
        task=task,
        status=TaskProgress.Status.COMPLETED,
    ).exists()


def get_level_tasks_context(learner, level):
    tasks = get_level_tasks(level)

    task_items = []
    current_task = None
    previous_completed = True

    for task in tasks:
        progress = TaskProgress.objects.filter(
            learner=learner,
            task=task,
        ).first()

        completed = bool(
            progress and progress.status == TaskProgress.Status.COMPLETED
        )

        if completed:
            status = 'completed'
        elif previous_completed and current_task is None:
            status = 'current'
            current_task = task
        else:
            status = 'locked'

        task_items.append({
            'task': task,
            'progress': progress,
            'status': status,
            'is_completed': completed,
            'is_current': status == 'current',
            'is_locked': status == 'locked',
        })

        previous_completed = completed

    completed_tasks = sum(1 for item in task_items if item['is_completed'])
    total_tasks = len(task_items)

    progress_percent = 0

    if total_tasks:
        progress_percent = round((completed_tasks / total_tasks) * 100)

    return {
        'level': level,
        'task_items': task_items,
        'current_task': current_task,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'progress_percent': progress_percent,
    }


def can_learner_access_task(learner, task):
    context = get_level_tasks_context(learner, task.level)

    for item in context['task_items']:
        if item['task'].id == task.id:
            return not item['is_locked']

    return False
