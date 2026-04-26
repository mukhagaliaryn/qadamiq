from django.utils import timezone

from core.models import (
    Level,
    LevelProgress,
    Module,
    ModuleProgress,
    SubjectProgress,
    Task,
    TaskProgress,
)


def get_task_progress(learner, task):
    progress, _ = TaskProgress.objects.get_or_create(
        learner=learner,
        task=task,
        defaults={
            'status': TaskProgress.Status.UNLOCKED,
        },
    )

    if progress.status == TaskProgress.Status.LOCKED:
        progress.status = TaskProgress.Status.UNLOCKED
        progress.save(update_fields=['status', 'updated_at'])

    return progress


def mark_task_started(learner, task):
    progress = get_task_progress(learner, task)

    if progress.status == TaskProgress.Status.UNLOCKED:
        progress.status = TaskProgress.Status.IN_PROGRESS
        progress.started_at = timezone.now()
        progress.save(update_fields=['status', 'started_at', 'updated_at'])

    return progress


def mark_task_completed(learner, task, answer_data):
    progress = get_task_progress(learner, task)

    progress.status = TaskProgress.Status.COMPLETED
    progress.attempts_count += 1
    progress.last_answer_data = answer_data

    if not progress.started_at:
        progress.started_at = timezone.now()

    progress.completed_at = timezone.now()
    progress.save()

    refresh_learning_progress(learner, task)

    return progress


def mark_task_failed_attempt(learner, task, answer_data):
    progress = get_task_progress(learner, task)

    progress.status = TaskProgress.Status.IN_PROGRESS
    progress.attempts_count += 1
    progress.last_answer_data = answer_data

    if not progress.started_at:
        progress.started_at = timezone.now()

    progress.save()

    return progress


def refresh_learning_progress(learner, task):
    level = task.level
    module = level.module
    subject = module.subject

    level_tasks = Task.objects.filter(
        level=level,
        is_active=True,
    )

    level_completed = not level_tasks.exclude(
        progresses__learner=learner,
        progresses__status=TaskProgress.Status.COMPLETED,
    ).exists()

    level_progress, _ = LevelProgress.objects.get_or_create(
        learner=learner,
        level=level,
    )

    level_progress.is_unlocked = True
    level_progress.is_started = True
    level_progress.is_completed = level_completed

    if not level_progress.started_at:
        level_progress.started_at = timezone.now()

    if level_completed:
        level_progress.completed_at = timezone.now()

    level_progress.save()

    module_levels = Level.objects.filter(
        module=module,
        is_active=True,
    )

    module_completed = not module_levels.exclude(
        progresses__learner=learner,
        progresses__is_completed=True,
    ).exists()

    module_progress, _ = ModuleProgress.objects.get_or_create(
        learner=learner,
        module=module,
    )

    module_progress.is_unlocked = True
    module_progress.is_started = True
    module_progress.is_completed = module_completed

    if not module_progress.started_at:
        module_progress.started_at = timezone.now()

    if module_completed:
        module_progress.completed_at = timezone.now()

    module_progress.save()

    subject_modules = Module.objects.filter(
        subject=subject,
        is_active=True,
    )

    subject_completed = not subject_modules.exclude(
        progresses__learner=learner,
        progresses__is_completed=True,
    ).exists()

    subject_progress, _ = SubjectProgress.objects.get_or_create(
        learner=learner,
        subject=subject,
    )

    subject_progress.is_started = True
    subject_progress.is_completed = subject_completed

    if not subject_progress.started_at:
        subject_progress.started_at = timezone.now()

    if subject_completed:
        subject_progress.completed_at = timezone.now()

    subject_progress.save()
    