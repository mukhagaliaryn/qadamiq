import random
from core.models import MatchingPair, MatchingTask, TestTask, TaskProgress, OrderingTask, OrderingItem, AudioSubmission, \
    AudioTask
from .progress import (
    mark_task_completed,
    mark_task_failed_attempt,
    mark_task_started,
)


# Test tasks
# ----------------------------------------------------------------------------------------------------------------------
def get_test_task_context(learner, task):
    test_task = TestTask.objects.select_related('task').get(
        task=task,
        is_active=True,
    )

    questions = test_task.questions.prefetch_related('answers').order_by('order', 'id')
    progress = mark_task_started(learner, task)

    return {
        'task': task,
        'test_task': test_task,
        'questions': questions,
        'progress': progress,
    }


def check_test_task_answers(learner, task, post_data):
    test_task = TestTask.objects.get(
        task=task,
        is_active=True,
    )
    questions = test_task.questions.prefetch_related('answers').order_by('order', 'id')
    answer_data = {
        'questions': [],
    }
    all_correct = True
    for question in questions:
        correct_answer_ids = set(
            question.answers.filter(is_correct=True).values_list('id', flat=True)
        )
        field_name = f'question_{question.id}'
        if test_task.allow_multiple_answers:
            selected_answer_ids = set(
                int(answer_id)
                for answer_id in post_data.getlist(field_name)
            )
        else:
            selected_value = post_data.get(field_name)
            selected_answer_ids = {int(selected_value)} if selected_value else set()

        question_is_correct = selected_answer_ids == correct_answer_ids

        if not question_is_correct:
            all_correct = False

        answer_data['questions'].append({
            'question_id': question.id,
            'selected_answer_ids': list(selected_answer_ids),
            'correct_answer_ids': list(correct_answer_ids),
            'is_correct': question_is_correct,
        })

    result_items = []
    for question in questions:
        saved_question = next(
            (
                item for item in answer_data['questions']
                if item['question_id'] == question.id
            ),
            None,
        )
        selected_ids = set(saved_question['selected_answer_ids']) if saved_question else set()
        correct_ids = set(saved_question['correct_answer_ids']) if saved_question else set()

        result_items.append({
            'question': question,
            'selected_ids': selected_ids,
            'correct_ids': correct_ids,
            'is_correct': selected_ids == correct_ids,
        })

    if all_correct:
        mark_task_completed(learner, task, answer_data)
    else:
        mark_task_failed_attempt(learner, task, answer_data)

    return {
        'is_correct': all_correct,
        'result_items': result_items,
        'answer_data': answer_data,
    }


def get_test_saved_result(learner, task):
    progress = TaskProgress.objects.filter(
        learner=learner,
        task=task,
        status=TaskProgress.Status.COMPLETED,
    ).first()

    if not progress or not progress.last_answer_data:
        return None

    test_task = TestTask.objects.get(
        task=task,
        is_active=True,
    )

    questions = test_task.questions.prefetch_related('answers').order_by('order', 'id')

    result_items = []

    for question in questions:
        saved_question = next(
            (
                item for item in progress.last_answer_data.get('questions', [])
                if item.get('question_id') == question.id
            ),
            None,
        )

        selected_ids = set(saved_question.get('selected_answer_ids', [])) if saved_question else set()
        correct_ids = set(saved_question.get('correct_answer_ids', [])) if saved_question else set()

        result_items.append({
            'question': question,
            'selected_ids': selected_ids,
            'correct_ids': correct_ids,
            'is_correct': selected_ids == correct_ids,
        })

    return {
        'is_correct': True,
        'result_items': result_items,
        'answer_data': progress.last_answer_data,
        'is_saved_result': True,
    }


# Matching tasks
# ----------------------------------------------------------------------------------------------------------------------
def get_matching_task_context(learner, task):
    matching_task = MatchingTask.objects.get(
        task=task,
        is_active=True,
    )
    pairs = list(
        MatchingPair.objects.filter(
            matching=matching_task,
        ).order_by('order', 'id')
    )
    right_options = pairs.copy()
    random.shuffle(right_options)

    rows = [
        {
            'pair': pair,
            'option': right_options[index],
        }
        for index, pair in enumerate(pairs)
    ]
    progress = mark_task_started(learner, task)
    return {
        'task': task,
        'matching_task': matching_task,
        'pairs': pairs,
        'rows': rows,
        'progress': progress,
    }


def check_matching_task_answers(learner, task, post_data):
    matching_task = MatchingTask.objects.get(
        task=task,
        is_active=True,
    )

    pairs = MatchingPair.objects.filter(
        matching=matching_task,
    ).order_by('order', 'id')

    answer_data = {
        'pairs': [],
    }

    result_items = []
    all_correct = True

    for pair in pairs:
        field_name = f'pair_{pair.id}'
        selected_id = post_data.get(field_name)

        selected_pair = None

        if selected_id:
            selected_pair = MatchingPair.objects.filter(
                id=selected_id,
                matching=matching_task,
            ).first()

        is_correct = str(pair.id) == str(selected_id)

        if not is_correct:
            all_correct = False

        answer_data['pairs'].append({
            'pair_id': pair.id,
            'selected_id': selected_id,
            'is_correct': is_correct,
        })

        result_items.append({
            'pair': pair,
            'selected_pair': selected_pair,
            'is_correct': is_correct,
        })

    if all_correct:
        mark_task_completed(learner, task, answer_data)
    else:
        mark_task_failed_attempt(learner, task, answer_data)

    return {
        'is_correct': all_correct,
        'result_items': result_items,
        'answer_data': answer_data,
    }


def get_matching_saved_result(learner, task):
    progress = TaskProgress.objects.filter(
        learner=learner,
        task=task,
        status=TaskProgress.Status.COMPLETED,
    ).first()

    if not progress or not progress.last_answer_data:
        return None

    matching_task = MatchingTask.objects.get(
        task=task,
        is_active=True,
    )

    result_items = []

    for answer in progress.last_answer_data.get('pairs', []):
        pair = MatchingPair.objects.filter(
            id=answer.get('pair_id'),
            matching=matching_task,
        ).first()

        selected_pair = MatchingPair.objects.filter(
            id=answer.get('selected_id'),
            matching=matching_task,
        ).first()

        if pair:
            result_items.append({
                'pair': pair,
                'selected_pair': selected_pair,
                'is_correct': answer.get('is_correct', False),
            })

    return {
        'is_correct': True,
        'result_items': result_items,
        'answer_data': progress.last_answer_data,
        'is_saved_result': True,
    }


# Ordering tasks
# ----------------------------------------------------------------------------------------------------------------------
def get_ordering_task_context(learner, task):
    ordering_tasks = list(
        OrderingTask.objects.filter(
            task=task,
            is_active=True,
        ).prefetch_related('items').order_by('order', 'id')
    )

    rows = []

    for ordering_task in ordering_tasks:
        items = list(
            ordering_task.items.all().order_by('correct_order', 'id')
        )

        shuffled_items = items.copy()
        random.shuffle(shuffled_items)

        rows.append({
            'ordering_task': ordering_task,
            'items': items,
            'shuffled_items': shuffled_items,
        })

    progress = mark_task_started(learner, task)

    return {
        'task': task,
        'ordering_tasks': ordering_tasks,
        'rows': rows,
        'progress': progress,
    }


def check_ordering_task_answers(learner, task, post_data):
    ordering_tasks = OrderingTask.objects.filter(
        task=task,
        is_active=True,
    ).prefetch_related('items').order_by('order', 'id')

    answer_data = {
        'ordering_tasks': [],
    }

    result_items = []
    all_correct = True

    for ordering_task in ordering_tasks:
        items = list(
            ordering_task.items.all().order_by('correct_order', 'id')
        )

        correct_order_ids = [item.id for item in items]

        field_name = f'order_{ordering_task.id}[]'
        submitted_ids = post_data.getlist(field_name)
        submitted_ids = [int(item_id) for item_id in submitted_ids]

        is_correct = submitted_ids == correct_order_ids

        if not is_correct:
            all_correct = False

        ordering_result_items = []

        for index, item_id in enumerate(submitted_ids):
            item = next((candidate for candidate in items if candidate.id == item_id), None)

            ordering_result_items.append({
                'item': item,
                'position': index,
                'is_correct': (
                    index < len(correct_order_ids)
                    and correct_order_ids[index] == item_id
                ),
            })

        answer_data['ordering_tasks'].append({
            'ordering_task_id': ordering_task.id,
            'submitted_ids': submitted_ids,
            'correct_ids': correct_order_ids,
            'is_correct': is_correct,
        })

        result_items.append({
            'ordering_task': ordering_task,
            'is_correct': is_correct,
            'items': ordering_result_items,
        })

    if all_correct:
        mark_task_completed(learner, task, answer_data)
    else:
        mark_task_failed_attempt(learner, task, answer_data)

    return {
        'is_correct': all_correct,
        'result_items': result_items,
        'answer_data': answer_data,
    }


def get_ordering_saved_result(learner, task):
    progress = TaskProgress.objects.filter(
        learner=learner,
        task=task,
        status=TaskProgress.Status.COMPLETED,
    ).first()

    if not progress or not progress.last_answer_data:
        return None

    ordering_tasks = OrderingTask.objects.filter(
        task=task,
        is_active=True,
    ).prefetch_related('items').order_by('order', 'id')

    result_items = []

    for ordering_task in ordering_tasks:
        saved_data = next(
            (
                item for item in progress.last_answer_data.get('ordering_tasks', [])
                if item.get('ordering_task_id') == ordering_task.id
            ),
            None,
        )

        if not saved_data:
            continue

        items = list(
            ordering_task.items.all().order_by('correct_order', 'id')
        )

        submitted_ids = saved_data.get('submitted_ids', [])

        ordering_result_items = []

        for index, item_id in enumerate(submitted_ids):
            item = next(
                (candidate for candidate in items if candidate.id == item_id),
                None,
            )

            correct_ids = saved_data.get('correct_ids', [])

            ordering_result_items.append({
                'item': item,
                'position': index,
                'is_correct': (
                    index < len(correct_ids)
                    and correct_ids[index] == item_id
                ),
            })

        result_items.append({
            'ordering_task': ordering_task,
            'is_correct': saved_data.get('is_correct', False),
            'items': ordering_result_items,
        })

    return {
        'is_correct': True,
        'result_items': result_items,
        'answer_data': progress.last_answer_data,
        'is_saved_result': True,
    }


# Audio tasks
# ----------------------------------------------------------------------------------------------------------------------
def get_audio_task_context(learner, task):
    audio_task = AudioTask.objects.get(
        task=task,
        is_active=True,
    )

    submission = AudioSubmission.objects.filter(
        learner=learner,
        task=task,
    ).first()

    progress = mark_task_started(learner, task)

    return {
        'task': task,
        'audio_task': audio_task,
        'submission': submission,
        'progress': progress,
    }


def save_audio_submission(learner, task, uploaded_file):
    submission, _ = AudioSubmission.objects.update_or_create(
        learner=learner,
        task=task,
        defaults={
            'title': task.title,
            'audio_file': uploaded_file,
        },
    )

    return submission


def complete_audio_task(learner, task, checklist_data):
    answer_data = {
        'checklist': checklist_data,
    }

    return mark_task_completed(learner, task, answer_data)


def get_audio_saved_result(learner, task):
    progress = TaskProgress.objects.filter(
        learner=learner,
        task=task,
        status=TaskProgress.Status.COMPLETED,
    ).first()

    if not progress:
        return None

    submission = AudioSubmission.objects.filter(
        learner=learner,
        task=task,
    ).first()

    if not submission:
        return None

    return {
        'is_correct': True,
        'submission': submission,
        'answer_data': progress.last_answer_data or {},
        'is_saved_result': True,
    }
