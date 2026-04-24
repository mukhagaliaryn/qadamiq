from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


# Classroom
# ----------------------------------------------------------------------------------------------------------------------
class Classroom(models.Model):
    name = models.CharField(
        _('Название класса'),
        max_length=255,
        help_text=_('Например: 3А, 4Б или подготовительная группа.')
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Преподаватель'),
        on_delete=models.CASCADE,
        related_name='owned_classrooms',
        help_text=_('Учитель, отвечающий за этот класс.')
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Обучающиеся'),
        related_name='classrooms',
        blank=True,
        help_text=_('Ученики обучающиеся в этом классе.')
    )

    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Класс')
        verbose_name_plural = _('Учебные классы')
        ordering = ['name']

    def clean(self):
        super().clean()

        if self.teacher and not self.teacher.is_teacher():
            raise ValidationError({
                'teacher': _('Владельцем класса должен быть преподаватель.')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
