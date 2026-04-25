from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import TimeStampedModel
from core.models.learning import Subject, Module, Level, Task


class SubjectProgress(TimeStampedModel):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Ученик'),
        on_delete=models.CASCADE,
        related_name='subject_progresses',
    )
    subject = models.ForeignKey(
        Subject,
        verbose_name=_('Предмет'),
        on_delete=models.CASCADE,
        related_name='progresses',
    )
    is_started = models.BooleanField(_('Начат'), default=False)
    is_completed = models.BooleanField(_('Завершён'), default=False)
    started_at = models.DateTimeField(_('Дата начала'), blank=True, null=True)
    completed_at = models.DateTimeField(_('Дата завершения'), blank=True, null=True)

    class Meta:
        verbose_name = _('Прогресс по предмету')
        verbose_name_plural = _('Прогресс по предметам')
        constraints = [
            models.UniqueConstraint(
                fields=['learner', 'subject'],
                name='unique_subject_progress_per_learner',
            ),
        ]

    def __str__(self):
        return f'{self.learner} — {self.subject}'


class ModuleProgress(TimeStampedModel):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Ученик'),
        on_delete=models.CASCADE,
        related_name='module_progresses',
    )
    module = models.ForeignKey(
        Module,
        verbose_name=_('Модуль'),
        on_delete=models.CASCADE,
        related_name='progresses',
    )
    is_unlocked = models.BooleanField(_('Открыт'), default=False)
    is_started = models.BooleanField(_('Начат'), default=False)
    is_completed = models.BooleanField(_('Завершён'), default=False)
    started_at = models.DateTimeField(_('Дата начала'), blank=True, null=True)
    completed_at = models.DateTimeField(_('Дата завершения'), blank=True, null=True)

    class Meta:
        verbose_name = _('Прогресс по модулю')
        verbose_name_plural = _('Прогресс по модулям')
        constraints = [
            models.UniqueConstraint(
                fields=['learner', 'module'],
                name='unique_module_progress_per_learner',
            ),
        ]

    def __str__(self):
        return f'{self.learner} — {self.module}'


class LevelProgress(TimeStampedModel):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Ученик'),
        on_delete=models.CASCADE,
        related_name='level_progresses',
    )
    level = models.ForeignKey(
        Level,
        verbose_name=_('Уровень'),
        on_delete=models.CASCADE,
        related_name='progresses',
    )
    is_unlocked = models.BooleanField(_('Открыт'), default=False)
    is_started = models.BooleanField(_('Начат'), default=False)
    is_completed = models.BooleanField(_('Завершён'), default=False)
    started_at = models.DateTimeField(_('Дата начала'), blank=True, null=True)
    completed_at = models.DateTimeField(_('Дата завершения'), blank=True, null=True)

    class Meta:
        verbose_name = _('Прогресс по уровню')
        verbose_name_plural = _('Прогресс по уровням')
        constraints = [
            models.UniqueConstraint(
                fields=['learner', 'level'],
                name='unique_level_progress_per_learner',
            ),
        ]

    def __str__(self):
        return f'{self.learner} — {self.level}'


class TaskProgress(TimeStampedModel):
    class Status(models.TextChoices):
        LOCKED = 'locked', _('Закрыто')
        UNLOCKED = 'unlocked', _('Открыто')
        IN_PROGRESS = 'in_progress', _('В процессе')
        COMPLETED = 'completed', _('Завершено')

    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Ученик'),
        on_delete=models.CASCADE,
        related_name='task_progresses',
    )
    task = models.ForeignKey(
        Task,
        verbose_name=_('Задание'),
        on_delete=models.CASCADE,
        related_name='progresses',
    )
    status = models.CharField(
        _('Статус'),
        max_length=30,
        choices=Status.choices,
        default=Status.LOCKED,
    )
    attempts_count = models.PositiveIntegerField(
        _('Количество попыток'),
        default=0,
    )
    last_answer_data = models.JSONField(
        _('Последний ответ'),
        blank=True,
        null=True,
    )
    started_at = models.DateTimeField(_('Дата начала'), blank=True, null=True)
    completed_at = models.DateTimeField(_('Дата завершения'), blank=True, null=True)

    class Meta:
        verbose_name = _('Прогресс по заданию')
        verbose_name_plural = _('Прогресс по заданиям')
        constraints = [
            models.UniqueConstraint(
                fields=['learner', 'task'],
                name='unique_task_progress_per_learner',
            ),
        ]

    def __str__(self):
        return f'{self.learner} — {self.task}'


class AudioSubmission(TimeStampedModel):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Ученик'),
        on_delete=models.CASCADE,
        related_name='audio_submissions',
    )
    task = models.ForeignKey(
        Task,
        verbose_name=_('Задание'),
        on_delete=models.CASCADE,
        related_name='audio_submissions',
    )
    title = models.CharField(
        _('Название аудиозаписи'),
        max_length=255,
    )
    audio_file = models.FileField(
        _('Аудиофайл'),
        upload_to='audio-submissions/',
    )

    class Meta:
        verbose_name = _('Аудиоответ')
        verbose_name_plural = _('Аудиоответы')
        constraints = [
            models.UniqueConstraint(
                fields=['learner', 'task'],
                name='unique_audio_submission_per_task',
            ),
        ]

    def __str__(self):
        return f'{self.learner} — {self.title}'
