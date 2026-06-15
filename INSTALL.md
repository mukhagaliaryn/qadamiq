# Qadam IQ — ИИ-тьютор (MVP) орнату

Бұл патч learner платформасына OpenAI негізіндегі ИИ-тьютор чатын қосады.
Барлық файлдар репозиторий түбіріне қатысты дұрыс жолдарда орналасқан —
қалтаны жобаңыздың үстіне көшіріп қойыңыз.

## Жаңа файлдар
- core/models/tutor.py
- core/migrations/0008_tutorconversation_tutormessage.py
- core/admin/tutor.py
- apps/dashboard/learner/services/tutor_eval.py   (жанама әсерсіз баға беруші)
- apps/dashboard/learner/services/tutor.py         (промпт + OpenAI шақыруы)
- apps/dashboard/learner/views/tutor.py            (JSON endpoint)
- ui/templates/app/dashboard/learner/tasks/partials/tutor_panel.html  (чат UI)

## Өзгертілген файлдар
- core/models/__init__.py        (модельдерді экспорттау)
- core/admin/__init__.py          (admin тіркеу)
- apps/dashboard/learner/urls.py  (tasks/<id>/tutor/ маршруты)
- config/settings.py              (OPENAI_API_KEY, TUTOR_OPENAI_MODEL)
- requirements.txt                (openai)
- ui/templates/.../tasks/{ordering,test,matching,audio}.html  (панель include)

## Орнату қадамдары
1) pip install -r requirements.txt
2) .env файлына қосыңыз:
       OPENAI_API_KEY=sk-...
       TUTOR_OPENAI_MODEL=gpt-4o-mini   # қаласаңыз
3) python manage.py migrate
4) Серверді қайта іске қосып, оқушымен кез келген тапсырманы ашыңыз —
   «ИИ-помощник» панелі көрінеді.

## Қосымша баптаулар (settings.py, міндетті емес)
TUTOR_TEMPERATURE, TUTOR_MAX_TOKENS, TUTOR_MAX_HISTORY,
TUTOR_MAX_MESSAGES_PER_TASK, TUTOR_COOLDOWN_SECONDS — сервисте әдепкі мәндері бар.
