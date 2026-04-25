from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from core.models import Classroom, ClassroomSubject


class ClassroomSubjectInline(TabularInline):
    model = ClassroomSubject
    extra = 0
    fields = ('subject', 'assigned_by', 'is_active', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


@admin.register(Classroom)
class ClassroomAdmin(ModelAdmin):
    list_display = ('name', 'teacher', 'student_count', 'subject_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'teacher__username', 'teacher__first_name', 'teacher__last_name')
    filter_horizontal = ('students',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClassroomSubjectInline]

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'teacher', 'students'),
        }),
        (_('Время'), {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = _('Количество учеников')

    def subject_count(self, obj):
        return obj.classroom_subjects.count()
    subject_count.short_description = _('Количество предметов')


@admin.register(ClassroomSubject)
class ClassroomSubjectAdmin(ModelAdmin):
    list_display = ('classroom', 'subject', 'assigned_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'subject', 'created_at')
    search_fields = ('classroom__name', 'subject__title', 'assigned_by__username')
    readonly_fields = ('created_at',)

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('classroom', 'subject', 'assigned_by'),
        }),
        (_('Настройки'), {
            'fields': ('is_active',),
        }),
        (_('Время'), {
            'fields': ('created_at',),
        }),
    )
