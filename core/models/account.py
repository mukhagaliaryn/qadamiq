from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# User
# ----------------------------------------------------------------------------------------------------------------------
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        TEACHER = 'teacher', _('Преподаватель')
        LEARNER = 'learner', _('Ученик')

    role = models.CharField(
        _('Роль'),
        max_length=20,
        choices=Role.choices,
        default=Role.LEARNER,
        help_text=_('Показывает роль пользователя в системе.')
    )
    avatar = models.ImageField(
        _('Аватар'),
        upload_to='users/avatars/',
        blank=True,
        null=True,
        help_text=_('Фотография профиля пользователя.')
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    @property
    def full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.username

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_learner(self):
        return self.role == self.Role.LEARNER

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.full_name
