from core.models import Module, Subject, SubjectProgress, Task, TaskProgress


def get_learner_classrooms(learner):
    return learner.classrooms.all().order_by('name')


def get_available_subjects_for_learner(learner):
    return Subject.objects.filter(
        classroom_subjects__classroom__students=learner,
        classroom_subjects__is_active=True,
        is_active=True,
    ).distinct().order_by('order', 'title')


def get_subject_classrooms_for_learner(learner, subject):
    return learner.classrooms.filter(
        classroom_subjects__subject=subject,
        classroom_subjects__is_active=True,
    ).distinct().order_by('name')


def get_subject_modules(subject):
    return Module.objects.filter(
        subject=subject,
        is_active=True,
    ).order_by('order', 'id')


def get_subject_tasks(subject):
    return Task.objects.filter(
        level__module__subject=subject,
        is_active=True,
        level__is_active=True,
        level__module__is_active=True,
        level__module__subject__is_active=True,
    )


def get_subject_open_module(learner, subject):
    modules = get_subject_modules(subject)

    if not modules.exists():
        return None

    for module in modules:
        progress = module.progresses.filter(
            learner=learner,
            is_completed=True,
        ).first()

        if not progress:
            return module

    return modules.last()


def get_subject_summary(learner, subject):
    SubjectProgress.objects.get_or_create(
        learner=learner,
        subject=subject,
    )

    modules = get_subject_modules(subject)
    tasks = get_subject_tasks(subject)

    total_tasks = tasks.count()

    completed_tasks = TaskProgress.objects.filter(
        learner=learner,
        task__in=tasks,
        status=TaskProgress.Status.COMPLETED,
    ).count()

    progress_percent = 0

    if total_tasks:
        progress_percent = round((completed_tasks / total_tasks) * 100)

    return {
        'subject': subject,
        'classrooms': get_subject_classrooms_for_learner(learner, subject),
        'modules_count': modules.count(),
        'modules_preview': modules[:3],
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress_percent': progress_percent,
        'open_module': get_subject_open_module(learner, subject),
    }


def get_learner_dashboard_context(learner):
    classrooms = get_learner_classrooms(learner)
    subjects = get_available_subjects_for_learner(learner)

    subject_items = [
        get_subject_summary(learner, subject)
        for subject in subjects
    ]

    total_subjects = len(subject_items)
    total_tasks = sum(item['total_tasks'] for item in subject_items)
    completed_tasks = sum(item['completed_tasks'] for item in subject_items)

    overall_progress = 0

    if total_tasks:
        overall_progress = round((completed_tasks / total_tasks) * 100)

    return {
        'page_title': 'Панель ученика',
        'classrooms': classrooms,
        'subject_items': subject_items,
        'total_subjects': total_subjects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overall_progress': overall_progress,
    }
