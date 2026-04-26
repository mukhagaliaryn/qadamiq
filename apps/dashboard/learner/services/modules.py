from core.models import Level, LevelProgress, Subject, Module, ModuleProgress


def get_module_levels(module):
    return Level.objects.filter(
        module=module,
        is_active=True,
    ).order_by('order', 'id')


def is_level_completed(learner, level):
    return LevelProgress.objects.filter(
        learner=learner,
        level=level,
        is_completed=True,
    ).exists()


def get_module_levels_context(learner, module):
    levels = get_module_levels(module)

    level_items = []
    current_level = None
    previous_completed = True

    for level in levels:
        completed = is_level_completed(learner, level)

        if completed:
            status = 'completed'
        elif previous_completed and current_level is None:
            status = 'current'
            current_level = level
        else:
            status = 'locked'

        level_items.append({
            'level': level,
            'status': status,
            'is_completed': completed,
            'is_current': status == 'current',
            'is_locked': status == 'locked',
        })

        previous_completed = completed

    completed_count = sum(1 for item in level_items if item['is_completed'])
    total_count = len(level_items)

    progress_percent = 0

    if total_count:
        progress_percent = round((completed_count / total_count) * 100)

    return {
        'module': module,
        'level_items': level_items,
        'current_level': current_level,
        'completed_levels': completed_count,
        'total_levels': total_count,
        'progress_percent': progress_percent,
    }


def get_available_subjects_for_modules_page(learner):
    return Subject.objects.filter(
        classroom_subjects__classroom__students=learner,
        classroom_subjects__is_active=True,
        is_active=True,
    ).distinct().order_by('order', 'title')


def get_subject_modules(module_or_subject):
    return Module.objects.filter(
        subject=module_or_subject,
        is_active=True,
    ).order_by('order', 'id')


def is_module_completed(learner, module):
    return ModuleProgress.objects.filter(
        learner=learner,
        module=module,
        is_completed=True,
    ).exists()


def get_subject_modules_context(learner, subject):
    modules = get_subject_modules(subject)

    module_items = []
    current_module = None
    previous_completed = True

    for module in modules:
        completed = is_module_completed(learner, module)

        if completed:
            status = 'completed'
        elif previous_completed and current_module is None:
            status = 'current'
            current_module = module
        else:
            status = 'locked'

        module_items.append({
            'module': module,
            'status': status,
            'is_completed': completed,
            'is_current': status == 'current',
            'is_locked': status == 'locked',
        })

        previous_completed = completed

    return {
        'subject': subject,
        'module_items': module_items,
        'current_module': current_module,
        'modules_count': len(module_items),
    }


def get_modules_page_context(learner):
    subjects = get_available_subjects_for_modules_page(learner)

    subject_items = [
        get_subject_modules_context(learner, subject)
        for subject in subjects
    ]

    return {
        'page_title': 'Модули',
        'subject_items': subject_items,
    }
