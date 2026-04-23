from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


# Classroom
# ----------------------------------------------------------------------------------------------------------------------
class Classroom(models.Model):
    name = models.CharField(
        _('Class name'),
        max_length=255,
        help_text=_('For example: 3A, 4B or the preparatory group.')
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Teacher'),
        on_delete=models.CASCADE,
        related_name='owned_classrooms',
        help_text=_('The teacher in charge of this class.')
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Students'),
        related_name='classrooms',
        blank=True,
        help_text=_('Students enrolled in this class.')
    )

    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Classroom')
        verbose_name_plural = _('Classrooms')
        ordering = ['name']

    def clean(self):
        super().clean()

        if self.teacher and not self.teacher.is_teacher():
            raise ValidationError({
                'teacher': _('The Class owner must be a teacher.')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
