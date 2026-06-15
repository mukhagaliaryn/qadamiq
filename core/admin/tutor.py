from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from core.models import TutorConversation, TutorMessage


class TutorMessageInline(TabularInline):
    model = TutorMessage
    extra = 0
    fields = ('role', 'content', 'created_at')
    readonly_fields = ('role', 'content', 'created_at')
    ordering = ('created_at', 'id')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TutorConversation)
class TutorConversationAdmin(ModelAdmin):
    list_display = ('learner', 'task', 'message_count', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = (
        'learner__username',
        'learner__first_name',
        'learner__last_name',
        'task__title',
    )
    readonly_fields = ('learner', 'task', 'created_at', 'updated_at')
    inlines = [TutorMessageInline]

    def message_count(self, obj):
        return obj.messages.count()

    message_count.short_description = _('Сообщений')

    def has_add_permission(self, request):
        return False
