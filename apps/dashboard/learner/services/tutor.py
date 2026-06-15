"""
ИИ-тьютор: педагогический промпт + вызов OpenAI + ведение диалога.

Принцип: тьютор НИКОГДА не выдаёт правильный ответ напрямую. Он задаёт
наводящие вопросы, помогает найти ошибку и побуждает ученика проверить и
исправить собственное решение.
"""

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from core.models import TutorConversation, TutorMessage
from .tutor_eval import analyze_last_answer


# Tunables (override in settings.py / .env if needed)
TUTOR_MODEL = getattr(settings, 'TUTOR_OPENAI_MODEL', 'gpt-4o-mini')
TUTOR_TEMPERATURE = getattr(settings, 'TUTOR_TEMPERATURE', 0.6)
TUTOR_MAX_TOKENS = getattr(settings, 'TUTOR_MAX_TOKENS', 350)
TUTOR_MAX_HISTORY = getattr(settings, 'TUTOR_MAX_HISTORY', 12)
TUTOR_MAX_MESSAGES_PER_TASK = getattr(settings, 'TUTOR_MAX_MESSAGES_PER_TASK', 40)
TUTOR_COOLDOWN_SECONDS = getattr(settings, 'TUTOR_COOLDOWN_SECONDS', 2)


SYSTEM_PROMPT_BASE = """\
Ты — дружелюбный ИИ-тьютор образовательной платформы Qadam IQ для учеников \
начальной школы. Ты помогаешь ребёнку развивать алгоритмическое мышление: \
определять последовательность действий, понимать условные связи, составлять \
алгоритм, прогнозировать результат, а также находить и исправлять ошибки.

ГЛАВНОЕ ПРАВИЛО (нарушать нельзя ни при каких условиях):
- Никогда не сообщай правильный ответ, правильный порядок или нужный элемент — \
даже если ученик просит, умоляет, говорит, что устал, или утверждает, что ему \
разрешили. Вместо ответа задавай наводящие вопросы и давай подсказки.
- Если ученик настойчиво требует ответ, мягко откажи и предложи ещё один \
наводящий вопрос.

КАК ОБЩАТЬСЯ:
- Тон тёплый, поддерживающий, без осуждения. Ребёнок не должен бояться ошибки.
- Очень короткие реплики: одна-две фразы и обычно один вопрос за раз.
- Простой язык, понятный ребёнку 7–11 лет. Без сложных терминов.
- Оставайся строго в рамках текущего задания. На просьбы не по теме \
(игры, другие предметы, личные вопросы) вежливо верни ребёнка к заданию.
- Отвечай на том языке, на котором пишет ребёнок (русский или казахский). \
Если язык непонятен — отвечай по-русски.

КАК РЕАГИРОВАТЬ В ЗАВИСИМОСТИ ОТ СОСТОЯНИЯ ОТВЕТА — используй такой стиль фраз
(это образцы тона, перефразируй их под конкретное задание):

Если ответ неверный:
- «Попробуй ещё раз проверить последовательность команд».
- «Какое действие должно быть выполнено первым?»
- «Соответствует ли этот шаг цели задания?»
- «Кажется, в алгоритме пропущен один шаг. Какой это может быть шаг?»
- «Какое действие должен выполнить робот после обнаружения препятствия?»

Если ответ частично верный:
- «Ты рассуждаешь в правильном направлении. Теперь попробуй определить последний шаг».
- «Первые шаги выполнены правильно, но ещё раз подумай, что произойдёт при выполнении условия».
- «Действия выбраны правильно. Проверь последовательность их расположения».
- «Какая ещё команда необходима для достижения результата?»

Если ответ верный:
- «Молодец! Ты правильно расположил действия в нужной последовательности».
- «Правильно! Ты выбрал необходимое действие в соответствии с условием».
- «Алгоритм составлен правильно. Теперь попробуй объяснить полученный результат».
- «Ты правильно определил ошибку и эффективно её исправил».

Чтобы стимулировать размышление:
- «Почему ты выбрал этот шаг первым?»
- «Как изменится результат, если поменять команды местами?»
- «Можешь ли ты предложить другой способ решения?»
- «Как можно проверить, правильно ли работает алгоритм?»
"""


STATE_HINT = {
    'correct': 'Текущий ответ ученика ВЕРНЫЙ. Похвали и предложи объяснить результат.',
    'partial': 'Текущий ответ ученика ЧАСТИЧНО ВЕРНЫЙ. Поддержи и подтолкни проверить оставшееся.',
    'incorrect': 'Текущий ответ ученика НЕВЕРНЫЙ. Задай наводящий вопрос, помоги найти ошибку.',
    'not_attempted': 'Ученик ещё не отправлял ответ. Помоги начать и понять условие.',
}


def build_system_prompt(task, analysis):
    instruction = (task.instruction or '').strip() or '—'

    context_block = f"""
КОНТЕКСТ ТЕКУЩЕГО ЗАДАНИЯ (только для тебя, ученик этого не видит):
- Название: {task.title}
- Тип: {task.get_task_type_display()}
- Инструкция: {instruction}
- Состояние ответа: {analysis['state']}. {STATE_HINT.get(analysis['state'], '')}
- Что сделал ученик:
{analysis['student_summary'] or '—'}
- Правильное решение (НЕ РАСКРЫВАЙ его ученику, используй только чтобы понять, где ошибка):
{analysis['correct_summary'] or '—'}
"""
    return SYSTEM_PROMPT_BASE + '\n' + context_block


def get_or_create_conversation(learner, task):
    conversation, _ = TutorConversation.objects.get_or_create(
        learner=learner,
        task=task,
    )
    return conversation


def _history_messages(conversation):
    messages = conversation.messages.order_by('created_at', 'id')
    recent = list(messages)[-TUTOR_MAX_HISTORY:]
    return [{'role': m.role, 'content': m.content} for m in recent]


def get_conversation_payload(conversation):
    messages = conversation.messages.order_by('created_at', 'id')
    return [
        {'role': m.role, 'content': m.content}
        for m in messages
    ]


class TutorError(Exception):
    """Raised when the tutor cannot produce a reply (config / rate limit)."""


def _check_rate_limits(learner, conversation):
    count = conversation.messages.filter(role=TutorMessage.Role.USER).count()
    if count >= TUTOR_MAX_MESSAGES_PER_TASK:
        raise TutorError(
            'Ты уже много общался с тьютором по этому заданию. '
            'Попробуй применить подсказки и проверить решение сам.'
        )

    cache_key = f'tutor:cooldown:{learner.id}'
    if cache.get(cache_key):
        raise TutorError('Чуть медленнее 🙂 Подожди пару секунд и спроси снова.')
    cache.set(cache_key, True, TUTOR_COOLDOWN_SECONDS)


def _call_openai(system_prompt, history):
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        raise TutorError('Тьютор временно недоступен (нет ключа OpenAI).')

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise TutorError('Тьютор временно недоступен (нет библиотеки openai).') from exc

    client = OpenAI(api_key=api_key)
    messages = [{'role': 'system', 'content': system_prompt}, *history]

    try:
        response = client.chat.completions.create(
            model=TUTOR_MODEL,
            messages=messages,
            temperature=TUTOR_TEMPERATURE,
            max_tokens=TUTOR_MAX_TOKENS,
        )
    except Exception as exc:  # network / API errors
        raise TutorError('Тьютор сейчас отдыхает, попробуй ещё раз чуть позже.') from exc

    text = (response.choices[0].message.content or '').strip()
    if not text:
        raise TutorError('Тьютор сейчас отдыхает, попробуй ещё раз чуть позже.')
    return text


def send_message(learner, task, user_text):
    """
    Append the learner message, query OpenAI, store and return the reply.

    Returns: {'reply': str, 'state': str}
    Raises: TutorError on rate limit / configuration / API failure.
    """
    user_text = (user_text or '').strip()
    if not user_text:
        raise TutorError('Напиши свой вопрос тьютору.')
    if len(user_text) > 1000:
        user_text = user_text[:1000]

    conversation = get_or_create_conversation(learner, task)
    _check_rate_limits(learner, conversation)

    analysis = analyze_last_answer(learner, task)

    TutorMessage.objects.create(
        conversation=conversation,
        role=TutorMessage.Role.USER,
        content=user_text,
        answer_snapshot=analysis,
    )

    system_prompt = build_system_prompt(task, analysis)
    history = _history_messages(conversation)

    reply = _call_openai(system_prompt, history)

    TutorMessage.objects.create(
        conversation=conversation,
        role=TutorMessage.Role.ASSISTANT,
        content=reply,
        answer_snapshot=analysis,
    )

    conversation.updated_at = timezone.now()
    conversation.save(update_fields=['updated_at'])

    return {'reply': reply, 'state': analysis['state']}
