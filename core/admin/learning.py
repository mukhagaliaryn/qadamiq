from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from core.admin.mixins import LinkedAdminMixin
from core.models import (
    Subject,
    Module,
    Level,
    Task,
    TestTask,
    TestQuestion,
    TestAnswer,
    MatchingTask,
    MatchingPair,
    MatchingGroup,
    MatchingGroupItem,
    OrderingTask,
    OrderingItem,
    AudioTask,
)


# SubjectAdmin inlines
# ----------------------------------------------------------------------------------------------------------------------
class ModuleInline(LinkedAdminMixin, TabularInline):
    model = Module
    extra = 0
    fields = (
        'title',
        'slug',
        'order',
        'is_active',
        'module_link',
    )
    readonly_fields = (
        'module_link',
    )
    show_change_link = True

    def module_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    module_link.short_description = _('Ссылка')


# SubjectAdmin
@admin.register(Subject)
class SubjectAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'title')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ModuleInline]
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }


# ModuleAdmin inlines
# ----------------------------------------------------------------------------------------------------------------------
# LevelInline
class LevelInline(LinkedAdminMixin, TabularInline):
    model = Level
    extra = 0
    fields = (
        'title',
        'order',
        'is_active',
        'level_link',
    )
    readonly_fields = (
        'level_link',
    )
    show_change_link = True

    def level_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    level_link.short_description = _('Ссылка')


# ModuleAdmin
@admin.register(Module)
class ModuleAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('title', 'subject', 'order', 'is_active', 'created_at')
    list_filter = ('subject', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'subject__title')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('subject', 'order')
    readonly_fields = ('subject_link',)
    inlines = [LevelInline]
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def subject_link(self, obj):
        return self.parent_link(obj, 'subject', label_field='title')

    subject_link.short_description = _('Предмет')


# LevelAdmin inlines
# ----------------------------------------------------------------------------------------------------------------------
# TaskInline
class TaskInline(LinkedAdminMixin, TabularInline):
    model = Task
    extra = 0
    fields = (
        'title',
        'task_type',
        'order',
        'is_active',
        'task_link',
    )
    readonly_fields = (
        'task_link',
    )
    show_change_link = True

    def task_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    task_link.short_description = _('Ссылка')


# LevelAdmin
@admin.register(Level)
class LevelAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('title', 'module', 'order', 'is_active', 'created_at')
    list_filter = ('module__subject', 'module', 'is_active', 'created_at')
    search_fields = ('title', 'module__title', 'module__subject__title')
    ordering = ('module', 'order')
    readonly_fields = ('module_link',)
    inlines = [TaskInline]

    def module_link(self, obj):
        return self.parent_link(obj, 'module', label_field='title')

    module_link.short_description = _('Модуль')


# TaskAdmin inlines
# ----------------------------------------------------------------------------------------------------------------------
# TestTaskInline
class TestTaskInline(LinkedAdminMixin, TabularInline):
    model = TestTask
    extra = 0
    max_num = 1
    fields = (
        'allow_multiple_answers',
        'is_active',
        'test_task_link',
    )
    readonly_fields = (
        'test_task_link',
    )
    show_change_link = True

    def test_task_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    test_task_link.short_description = _('Ссылка')


# MatchingTaskInline
class MatchingTaskInline(LinkedAdminMixin, TabularInline):
    model = MatchingTask
    extra = 0
    max_num = 1
    fields = (
        'mode',
        'is_active',
        'matching_task_link',
    )
    readonly_fields = ('matching_task_link',)
    show_change_link = True

    def matching_task_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    matching_task_link.short_description = _('Ссылка')


# OrderingTaskInline
class OrderingTaskInline(LinkedAdminMixin, TabularInline):
    model = OrderingTask
    extra = 0
    fields = (
        'order',
        'description',
        'is_active',
        'ordering_task_link',
    )
    readonly_fields = ('ordering_task_link',)
    show_change_link = True
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def ordering_task_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    ordering_task_link.short_description = _('Ссылка')


# AudioTaskInline
class AudioTaskInline(LinkedAdminMixin, TabularInline):
    model = AudioTask
    extra = 0
    max_num = 1
    fields = (
        'content_text',
        'content_image',
        'content_audio',
        'is_active',
        'audio_task_link',
    )
    readonly_fields = ('audio_task_link',)
    show_change_link = True
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def audio_task_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    audio_task_link.short_description = _('Ссылка')


# TaskAdmin
@admin.register(Task)
class TaskAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('title', 'level', 'task_type', 'order', 'is_active', 'created_at')
    list_filter = ('task_type', 'level__module__subject', 'level__module', 'is_active')
    search_fields = ('title', 'instruction', 'content_text')
    ordering = ('level', 'order')
    readonly_fields = ('level_link',)
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.task_type == Task.TaskType.TEST:
            return [
                TestTaskInline,
            ]
        if obj.task_type == Task.TaskType.MATCHING:
            return [
                MatchingTaskInline,
            ]
        if obj.task_type == Task.TaskType.ORDERING:
            return [
                OrderingTaskInline,
            ]
        if obj.task_type == Task.TaskType.AUDIO:
            return [
                AudioTaskInline,
            ]
        return []

    def level_link(self, obj):
        return self.parent_link(obj, 'level', label_field='title')

    level_link.short_description = _('Уровень')



# TestTaskAdmin inlines
# ----------------------------------------------------------------------------------------------------------------------
# TestQuestionInline
class TestQuestionInline(LinkedAdminMixin, TabularInline):
    model = TestQuestion
    extra = 0
    fields = (
        'order',
        'content_text',
        'question_link',
    )
    readonly_fields = ('question_link',)
    show_change_link = True
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def question_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    question_link.short_description = _('Ссылка')


# TestTaskAdmin
@admin.register(TestTask)
class TestTaskAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('task', 'allow_multiple_answers', 'created_at')
    list_filter = ('allow_multiple_answers', 'created_at')
    search_fields = ('task__title',)
    readonly_fields = ('task_link',)
    inlines = [TestQuestionInline]

    def task_link(self, obj):
        return self.parent_link(obj, 'task', label_field='title')

    task_link.short_description = _('Задание')


# ---------------- TestQuestionAdmin inlines ----------------
# TestAnswerInline
class TestAnswerInline(TabularInline):
    model = TestAnswer
    extra = 0
    fields = (
        'content_text',
        'content_image',
        'content_audio',
        'is_correct',
    )
    show_change_link = True
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }


# TestQuestionAdmin
@admin.register(TestQuestion)
class TestQuestionAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('test', 'content_text', 'order', 'created_at')
    list_filter = ('test', 'created_at')
    search_fields = ('content_text', 'test__task__title')
    readonly_fields = ('test_link',)
    inlines = [TestAnswerInline]
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def test_link(self, obj):
        return self.parent_link(obj, 'test', label_field='task')

    test_link.short_description = _('Тест')


# MatchingTaskAdmin inlines
# ----------------------------------------------------------------------------------------------------------------------
# MatchingPairInline
class MatchingPairInline(LinkedAdminMixin, TabularInline):
    model = MatchingPair
    extra = 0
    fields = (
        'order',
        'left_text',
        'left_image',
        'left_audio',
        'pair_link',
    )
    readonly_fields = ('pair_link',)
    show_change_link = True
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def pair_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    pair_link.short_description = _('Ссылка')


# MatchingGroupInline
class MatchingGroupInline(LinkedAdminMixin, TabularInline):
    model = MatchingGroup
    extra = 0
    fields = (
        'order',
        'title',
        'content_text',
        'group_link',
    )
    readonly_fields = (
        'group_link',
    )
    show_change_link = True

    def group_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    group_link.short_description = _('Ссылка')


# MatchingTaskAdmin
@admin.register(MatchingTask)
class MatchingTaskAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('task', 'mode', 'created_at')
    list_filter = ('mode', 'created_at')
    search_fields = ('task__title',)
    readonly_fields = ('created_at', 'updated_at', 'task_link')
    inlines = [MatchingPairInline, MatchingGroupInline]

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.mode == MatchingTask.MatchingMode.PAIR:
            return [
                MatchingPairInline,
            ]
        if obj.mode == MatchingTask.MatchingMode.GROUP:
            return [
                MatchingGroupInline,
            ]
        return []

    def task_link(self, obj):
        return self.parent_link(obj, 'task', label_field='title')

    task_link.short_description = _('Задание')


# ---------------- MatchingPairAdmin ----------------
@admin.register(MatchingPair)
class MatchingPairAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('matching', 'left_text', 'right_text', 'order')
    list_filter = ('matching',)
    search_fields = ('left_text', 'right_text')
    readonly_fields = ('matching_link',)
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def matching_link(self, obj):
        return self.parent_link(obj, 'matching', label_field='task')

    matching_link.short_description = _('Задание на сопоставление')


# ---------------- MatchingGroupAdmin inlines ----------------
# MatchingGroupItemInline
class MatchingGroupItemInline(LinkedAdminMixin, TabularInline):
    model = MatchingGroupItem
    extra = 0
    fields = (
        'order',
        'content_text',
        'content_image',
        'content_audio',
        'item_link',
    )
    readonly_fields = (
        'item_link',
    )
    show_change_link = True

    def item_link(self, obj):
        return self.admin_link(obj, label=_('Подробнее'))

    item_link.short_description = _('Ссылка')


# MatchingGroupAdmin
@admin.register(MatchingGroup)
class MatchingGroupAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('title', 'matching', 'order')
    list_filter = ('matching',)
    search_fields = ('title', 'content_text')
    readonly_fields = (
        'created_at',
        'updated_at',
        'matching_link',
    )
    inlines = [MatchingGroupItemInline]

    def matching_link(self, obj):
        return self.parent_link(obj, 'matching', label_field='task')

    matching_link.short_description = _('Задание на сопоставление')


# ---------------- MatchingGroupItemAdmin ----------------
# MatchingGroupItemAdmin
@admin.register(MatchingGroupItem)
class MatchingGroupItemAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('group', 'content_text', 'order')
    list_filter = ('group',)
    search_fields = ('content_text',)
    readonly_fields = (
        'created_at',
        'updated_at',
        'group_link',
    )

    def group_link(self, obj):
        return self.parent_link(obj, 'group', label_field='title')

    group_link.short_description = _('Группа')


# OrderingTaskAdmin inlines
# ----------------------------------------------------------------------------------------------------------------------
# OrderingItemInline
class OrderingItemInline(LinkedAdminMixin, TabularInline):
    model = OrderingItem
    extra = 0
    fields = (
        'correct_order',
        'content_text',
        'content_image',
        'content_audio',
    )
    show_change_link = True
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }


# OrderingTaskAdmin
@admin.register(OrderingTask)
class OrderingTaskAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('task', 'created_at')
    search_fields = ('task__title',)
    readonly_fields = ('task_link',)
    inlines = [OrderingItemInline]
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def task_link(self, obj):
        return self.parent_link(obj, 'task', label_field='title')

    task_link.short_description = _('Задание')


# AudioTaskAdmin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(AudioTask)
class AudioTaskAdmin(LinkedAdminMixin, ModelAdmin):
    list_display = ('task', 'created_at')
    search_fields = ('task__title', 'content_text')
    readonly_fields = ('task_link',)
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget,
        },
    }

    def task_link(self, obj):
        return self.parent_link(obj, 'task', label_field='title')

    task_link.short_description = _('Задание')
