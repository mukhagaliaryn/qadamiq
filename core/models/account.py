from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# User
# ----------------------------------------------------------------------------------------------------------------------
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        TEACHER = 'teacher', _('Teacher')
        LEARNER = 'learner', _('Learner')

    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=Role.choices,
        default=Role.LEARNER,
        help_text=_('Shows the user\'s role in the system.')
    )
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='users/avatars/',
        blank=True,
        null=True,
        help_text=_('User profile picture.')
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

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
