"""
Pure, side-effect-free analysis of a learner's most recent answer.

Reads `TaskProgress.last_answer_data` (written by the existing
`check_*_task_answers` services) and turns it into a compact, structured
analysis the tutor can reason over:

    {
        'state': 'correct' | 'partial' | 'incorrect' | 'not_attempted',
        'attempts': int,
        'student_summary': str,   # what the learner did + what is right/wrong
        'correct_summary': str,   # the correct solution — FOR THE MODEL ONLY,
                                  # the prompt forbids revealing it to the child
    }

These functions never write to the database.
"""

from core.models import (
    AudioTask,
    MatchingPair,
    MatchingTask,
    OrderingTask,
    Task,
    TaskProgress,
    TestAnswer,
    TestQuestion,
    TestTask,
)


def _state_from_counts(correct, total):
    if total == 0:
        return 'not_attempted'
    if correct == 0:
        return 'incorrect'
    if correct == total:
        return 'correct'
    return 'partial'


def _text(value, fallback='[без текста]'):
    value = (value or '').strip()
    return value or fallback


def analyze_last_answer(learner, task):
    progress = TaskProgress.objects.filter(learner=learner, task=task).first()

    if not progress or not progress.last_answer_data:
        return {
            'state': 'not_attempted',
            'attempts': progress.attempts_count if progress else 0,
            'student_summary': 'Ученик ещё не отправлял ответ на это задание.',
            'correct_summary': '',
        }

    data = progress.last_answer_data
    attempts = progress.attempts_count

    if task.task_type == Task.TaskType.TEST:
        result = _analyze_test(task, data)
    elif task.task_type == Task.TaskType.MATCHING:
        result = _analyze_matching(task, data)
    elif task.task_type == Task.TaskType.ORDERING:
        result = _analyze_ordering(task, data)
    elif task.task_type == Task.TaskType.AUDIO:
        result = _analyze_audio(task, data)
    else:
        result = {
            'state': 'not_attempted',
            'student_summary': 'Тип задания не поддерживается тьютором.',
            'correct_summary': '',
        }

    result['attempts'] = attempts
    return result


def _analyze_test(task, data):
    test_task = TestTask.objects.filter(task=task).first()
    questions = data.get('questions', [])

    correct = sum(1 for q in questions if q.get('is_correct'))
    total = len(questions)

    student_lines = []
    correct_lines = []

    for entry in questions:
        question = TestQuestion.objects.filter(id=entry.get('question_id')).first()
        q_text = _text(question.content_text if question else None, '[вопрос]')

        selected = TestAnswer.objects.filter(id__in=entry.get('selected_answer_ids', []))
        correct_answers = TestAnswer.objects.filter(id__in=entry.get('correct_answer_ids', []))

        selected_text = ', '.join(_text(a.content_text) for a in selected) or '[ничего не выбрано]'
        correct_text = ', '.join(_text(a.content_text) for a in correct_answers) or '[нет данных]'
        mark = 'верно' if entry.get('is_correct') else 'неверно'

        student_lines.append(f'Вопрос: {q_text} | выбрано: {selected_text} | {mark}')
        correct_lines.append(f'Вопрос: {q_text} | правильно: {correct_text}')

    return {
        'state': _state_from_counts(correct, total),
        'student_summary': '\n'.join(student_lines),
        'correct_summary': '\n'.join(correct_lines),
    }


def _analyze_matching(task, data):
    matching_task = MatchingTask.objects.filter(task=task).first()
    pairs = data.get('pairs', [])

    correct = sum(1 for p in pairs if p.get('is_correct'))
    total = len(pairs)

    student_lines = []
    correct_lines = []

    for entry in pairs:
        pair = MatchingPair.objects.filter(id=entry.get('pair_id')).first()
        selected = MatchingPair.objects.filter(id=entry.get('selected_id')).first()

        if not pair:
            continue

        left = _text(pair.left_text, '[левый элемент]')
        chosen_right = _text(selected.right_text, '[не выбрано]') if selected else '[не выбрано]'
        right = _text(pair.right_text, '[правый элемент]')
        mark = 'верно' if entry.get('is_correct') else 'неверно'

        student_lines.append(f'{left} → ученик выбрал: {chosen_right} | {mark}')
        correct_lines.append(f'{left} = {right}')

    return {
        'state': _state_from_counts(correct, total),
        'student_summary': '\n'.join(student_lines),
        'correct_summary': '\n'.join(correct_lines),
    }


def _analyze_ordering(task, data):
    ordering_blocks = data.get('ordering_tasks', [])

    correct_blocks = sum(1 for b in ordering_blocks if b.get('is_correct'))
    total_blocks = len(ordering_blocks)

    student_lines = []
    correct_lines = []

    for block in ordering_blocks:
        ordering_task = OrderingTask.objects.filter(id=block.get('ordering_task_id')).first()
        if not ordering_task:
            continue

        items = {item.id: _text(item.content_text) for item in ordering_task.items.all()}
        description = _text(ordering_task.description, '[последовательность]')

        submitted = block.get('submitted_ids', [])
        correct_ids = block.get('correct_ids', [])

        submitted_texts = [items.get(i, '[?]') for i in submitted]
        correct_texts = [items.get(i, '[?]') for i in correct_ids]

        # Which positions the learner already placed correctly.
        wrong_positions = [
            index + 1
            for index, item_id in enumerate(submitted)
            if index >= len(correct_ids) or correct_ids[index] != item_id
        ]
        wrong_note = (
            'все позиции верны'
            if not wrong_positions
            else f'неверные позиции: {wrong_positions}'
        )

        student_lines.append(
            f'«{description}» | порядок ученика: {submitted_texts} | {wrong_note}'
        )
        correct_lines.append(f'«{description}» | правильный порядок: {correct_texts}')

    return {
        'state': _state_from_counts(correct_blocks, total_blocks),
        'student_summary': '\n'.join(student_lines),
        'correct_summary': '\n'.join(correct_lines),
    }


def _analyze_audio(task, data):
    audio_task = AudioTask.objects.filter(task=task).first()
    prompt = _text(audio_task.content_text if audio_task else None, '[аудиозадание]')
    checklist = data.get('checklist', {})

    answered = all(checklist.values()) if checklist else False

    return {
        'state': 'correct' if answered else 'partial',
        'student_summary': (
            f'Аудиозадание: {prompt}. Чек-лист самопроверки: {checklist or "не заполнен"}.'
        ),
        'correct_summary': 'Это устное задание — единственного правильного ответа нет.',
    }
