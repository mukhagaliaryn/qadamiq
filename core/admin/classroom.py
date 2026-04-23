from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from core.models import Classroom


@admin.register(Classroom)
class ClassroomAdmin(ModelAdmin):
    list_display = ('name', 'teacher', 'student_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'teacher__username', 'teacher__first_name', 'teacher__last_name')
    filter_horizontal = ('students',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Main information'), {
            'fields': ('name', 'teacher', 'students'),
        }),
        (_('Time signs'), {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = _('Student count')
