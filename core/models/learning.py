from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import TimeStampedModel


class ContentFieldsMixin(models.Model):
    content_text = models.TextField(
        _('Текст'),
        blank=True,
    )
    content_image = models.ImageField(
        _('Изображение'),
        upload_to='learning/images/',
        blank=True,
        null=True,
    )
    content_audio = models.FileField(
        _('Аудиофайл'),
        upload_to='learning/audio/',
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


# Subject models
# ----------------------------------------------------------------------------------------------------------------------
class Subject(TimeStampedModel):
    title = models.CharField(
        _('Название предмета'),
        max_length=255,
    )
    slug = models.SlugField(
        _('Слаг'),
        unique=True,
    )
    description = models.TextField(
        _('Описание'),
        blank=True,
    )
    cover_image = models.ImageField(
        _('Обложка'),
        upload_to='subjects/covers/',
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        _('Активен'),
        default=True,
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Предмет')
        verbose_name_plural = _('Предметы')
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Module(TimeStampedModel):
    subject = models.ForeignKey(
        Subject,
        verbose_name=_('Предмет'),
        on_delete=models.CASCADE,
        related_name='modules',
    )
    title = models.CharField(
        _('Название модуля'),
        max_length=255,
    )
    slug = models.SlugField(
        _('Слаг'),
    )
    description = models.TextField(
        _('Описание'),
        blank=True,
    )
    cover_image = models.ImageField(
        _('Обложка'),
        upload_to='modules/covers/',
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        _('Активен'),
        default=True,
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модули')
        ordering = ['subject', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['subject', 'slug'],
                name='unique_module_slug_per_subject',
            ),
        ]

    def __str__(self):
        return self.title


class Level(TimeStampedModel):
    module = models.ForeignKey(
        Module,
        verbose_name=_('Модуль'),
        on_delete=models.CASCADE,
        related_name='levels',
    )
    title = models.CharField(
        _('Название уровня'),
        max_length=255,
    )
    is_active = models.BooleanField(
        _('Активен'),
        default=True,
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Уровень')
        verbose_name_plural = _('Уровни')
        ordering = ['module', 'order']

    def __str__(self):
        return f'{self.module}: {self.title}'


# Task models
# ----------------------------------------------------------------------------------------------------------------------
class Task(TimeStampedModel):
    class TaskType(models.TextChoices):
        TEST = 'test', _('Тест')
        MATCHING = 'matching', _('Сопоставление')
        ORDERING = 'ordering', _('Правильная последовательность')
        AUDIO = 'audio', _('Аудиозапись')

    level = models.ForeignKey(
        Level,
        verbose_name=_('Уровень'),
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    title = models.CharField(
        _('Название задания'),
        max_length=255,
    )
    instruction = models.TextField(
        _('Инструкция'),
        blank=True,
    )
    task_type = models.CharField(
        _('Тип задания'),
        max_length=30,
        choices=TaskType.choices,
    )
    is_active = models.BooleanField(
        _('Активно'),
        default=True,
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Задание')
        verbose_name_plural = _('Задания')
        ordering = ['level', 'order']

    def __str__(self):
        return f'{self.level}: {self.title}'


# Task: Test models
# ----------------------------------------------------------------------------------------------------------------------
class TestTask(TimeStampedModel):
    task = models.OneToOneField(
        Task,
        verbose_name=_('Задание'),
        on_delete=models.CASCADE,
        related_name='test_task',
    )
    allow_multiple_answers = models.BooleanField(
        _('Разрешить несколько правильных ответов'),
        default=False,
    )
    is_active = models.BooleanField(
        _('Активно'),
        default=False,
    )

    class Meta:
        verbose_name = _('Тест')
        verbose_name_plural = _('Тесты')

    def __str__(self):
        return self.task.title


class TestQuestion(TimeStampedModel, ContentFieldsMixin):
    test = models.ForeignKey(
        TestTask,
        verbose_name=_('Тест'),
        on_delete=models.CASCADE,
        related_name='questions',
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Вопрос теста')
        verbose_name_plural = _('Вопросы теста')
        ordering = ['test', 'order']

    def __str__(self):
        return f'{self.test}: {self.content_text[:50]}'


class TestAnswer(TimeStampedModel, ContentFieldsMixin):
    question = models.ForeignKey(
        TestQuestion,
        verbose_name=_('Вопрос'),
        on_delete=models.CASCADE,
        related_name='answers',
    )
    is_correct = models.BooleanField(
        _('Правильный ответ'),
        default=False,
    )

    class Meta:
        verbose_name = _('Ответ теста')
        verbose_name_plural = _('Ответы теста')

    def __str__(self):
        return self.content_text[:50] or str(_('Ответ'))


# Task: Matching models
# ----------------------------------------------------------------------------------------------------------------------
class MatchingTask(TimeStampedModel):
    class MatchingMode(models.TextChoices):
        PAIR = 'pair', _('Один к одному')
        GROUP = 'group', _('Один ко многим')

    task = models.OneToOneField(
        Task,
        verbose_name=_('Задание'),
        on_delete=models.CASCADE,
        related_name='matching_task',
    )
    mode = models.CharField(
        _('Режим сопоставления'),
        max_length=20,
        choices=MatchingMode.choices,
    )
    is_active = models.BooleanField(
        _('Активно'),
        default=False,
    )

    class Meta:
        verbose_name = _('Задание на сопоставление')
        verbose_name_plural = _('Задания на сопоставление')

    def __str__(self):
        return self.task.title


class MatchingPair(TimeStampedModel):
    matching = models.ForeignKey(
        MatchingTask,
        verbose_name=_('Сопоставление'),
        on_delete=models.CASCADE,
        related_name='pairs',
    )

    left_text = models.TextField(_('Левый текст'), blank=True)
    left_image = models.ImageField(_('Левое изображение'), upload_to='matching/left/images/', blank=True, null=True)
    left_audio = models.FileField(_('Левый аудиофайл'), upload_to='matching/left/audio/', blank=True, null=True)

    right_text = models.TextField(_('Правый текст'), blank=True)
    right_image = models.ImageField(_('Правое изображение'), upload_to='matching/right/images/', blank=True, null=True)
    right_audio = models.FileField(_('Правый аудиофайл'), upload_to='matching/right/audio/', blank=True, null=True)

    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Пара сопоставления')
        verbose_name_plural = _('Пары сопоставления')
        ordering = ['matching', 'order']

    def __str__(self):
        return f'{self.left_text[:30]} = {self.right_text[:30]}'


class MatchingGroup(TimeStampedModel, ContentFieldsMixin):
    matching = models.ForeignKey(
        MatchingTask,
        verbose_name=_('Сопоставление'),
        on_delete=models.CASCADE,
        related_name='groups',
    )
    title = models.CharField(
        _('Название группы'),
        max_length=255,
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Группа сопоставления')
        verbose_name_plural = _('Группы сопоставления')
        ordering = ['matching', 'order']

    def __str__(self):
        return self.title


class MatchingGroupItem(TimeStampedModel, ContentFieldsMixin):
    group = models.ForeignKey(
        MatchingGroup,
        verbose_name=_('Группа'),
        on_delete=models.CASCADE,
        related_name='items',
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Элемент группы')
        verbose_name_plural = _('Элементы группы')
        ordering = ['group', 'order']

    def __str__(self):
        return self.content_text[:50] or str(_('Элемент'))


# Task: Ordering models
# ----------------------------------------------------------------------------------------------------------------------
class OrderingTask(TimeStampedModel):
    task = models.ForeignKey(
        Task,
        verbose_name=_('Задание'),
        on_delete=models.CASCADE,
        related_name='ordering_task',
    )
    description = models.TextField(
        _('Описание'),
    )
    is_active = models.BooleanField(
        _('Активно'),
        default=True,
    )
    order = models.PositiveIntegerField(
        _('Порядок'),
        default=0,
    )

    class Meta:
        verbose_name = _('Задание на последовательность')
        verbose_name_plural = _('Задания на последовательность')

    def __str__(self):
        return self.task.title


class OrderingItem(TimeStampedModel, ContentFieldsMixin):
    ordering = models.ForeignKey(
        OrderingTask,
        verbose_name=_('Последовательность'),
        on_delete=models.CASCADE,
        related_name='items',
    )
    correct_order = models.PositiveIntegerField(
        _('Правильный порядок'),
    )

    class Meta:
        verbose_name = _('Элемент последовательности')
        verbose_name_plural = _('Элементы последовательности')
        ordering = ['ordering', 'correct_order']

    def __str__(self):
        return f'{self.correct_order}. {self.content_text[:50]}'


# Task: Audio models
# ----------------------------------------------------------------------------------------------------------------------
class AudioTask(TimeStampedModel, ContentFieldsMixin):
    task = models.OneToOneField(
        Task,
        verbose_name=_('Задание'),
        on_delete=models.CASCADE,
        related_name='audio_task',
    )
    is_active = models.BooleanField(
        _('Активно'),
        default=False,
    )

    class Meta:
        verbose_name = _('Задание с аудиозаписью')
        verbose_name_plural = _('Задания с аудиозаписью')

    def __str__(self):
        return self.task.title
