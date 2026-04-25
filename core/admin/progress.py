from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from core.models import (
    SubjectProgress,
    ModuleProgress,
    LevelProgress,
    TaskProgress,
    AudioSubmission,
)


@admin.register(SubjectProgress)
class SubjectProgressAdmin(ModelAdmin):
    list_display = ('learner', 'subject', 'is_started', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('is_started', 'is_completed', 'subject')
    search_fields = ('learner__username', 'learner__first_name', 'learner__last_name', 'subject__title')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('learner', 'subject'),
        }),
        (_('Статус'), {
            'fields': ('is_started', 'is_completed', 'started_at', 'completed_at'),
        }),
        (_('Время'), {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(ModuleProgress)
class ModuleProgressAdmin(ModelAdmin):
    list_display = ('learner', 'module', 'is_unlocked', 'is_started', 'is_completed')
    list_filter = ('is_unlocked', 'is_started', 'is_completed', 'module__subject')
    search_fields = ('learner__username', 'learner__first_name', 'learner__last_name', 'module__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LevelProgress)
class LevelProgressAdmin(ModelAdmin):
    list_display = ('learner', 'level', 'is_unlocked', 'is_started', 'is_completed')
    list_filter = ('is_unlocked', 'is_started', 'is_completed', 'level__module__subject')
    search_fields = ('learner__username', 'learner__first_name', 'learner__last_name', 'level__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TaskProgress)
class TaskProgressAdmin(ModelAdmin):
    list_display = ('learner', 'task', 'status', 'attempts_count', 'started_at', 'completed_at')
    list_filter = ('status', 'task__task_type', 'task__level__module__subject')
    search_fields = ('learner__username', 'learner__first_name', 'learner__last_name', 'task__title')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('learner', 'task'),
        }),
        (_('Статус'), {
            'fields': ('status', 'attempts_count', 'last_answer_data'),
        }),
        (_('Время выполнения'), {
            'fields': ('started_at', 'completed_at'),
        }),
        (_('Время'), {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(AudioSubmission)
class AudioSubmissionAdmin(ModelAdmin):
    list_display = ('learner', 'task', 'title', 'created_at')
    list_filter = ('created_at', 'task__level__module__subject')
    search_fields = ('learner__username', 'learner__first_name', 'learner__last_name', 'title', 'task__title')
    readonly_fields = ('created_at', 'updated_at')
