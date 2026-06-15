from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import TimeStampedModel
from core.models.learning import Task


class TutorConversation(TimeStampedModel):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Ученик'),
        on_delete=models.CASCADE,
        related_name='tutor_conversations',
    )
    task = models.ForeignKey(
        Task,
        verbose_name=_('Задание'),
        on_delete=models.CASCADE,
        related_name='tutor_conversations',
    )

    class Meta:
        verbose_name = _('Диалог с ИИ-тьютором')
        verbose_name_plural = _('Диалоги с ИИ-тьютором')
        constraints = [
            models.UniqueConstraint(
                fields=['learner', 'task'],
                name='unique_tutor_conversation_per_task',
            ),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.learner} — {self.task}'


class TutorMessage(TimeStampedModel):
    class Role(models.TextChoices):
        USER = 'user', _('Ученик')
        ASSISTANT = 'assistant', _('ИИ-тьютор')

    conversation = models.ForeignKey(
        TutorConversation,
        verbose_name=_('Диалог'),
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(
        _('Роль'),
        max_length=20,
        choices=Role.choices,
    )
    content = models.TextField(
        _('Текст'),
    )
    # Snapshot of the learner's answer analysis at the moment this message
    # was produced (state + per-step correctness). Stored for transparency,
    # teacher review and debugging. Never shown to the learner directly.
    answer_snapshot = models.JSONField(
        _('Снимок ответа'),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('Сообщение тьютора')
        verbose_name_plural = _('Сообщения тьютора')
        ordering = ['conversation', 'created_at', 'id']

    def __str__(self):
        return f'{self.get_role_display()}: {self.content[:50]}'
