from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UFModelAdmin
from unfold.forms import UserCreationForm
from core.models import User
from django.contrib.auth.models import Group


# UserAdmin
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin, UFModelAdmin):
    list_display = ('avatar_preview', 'full_name_display', 'username', 'email', 'role', 'is_active', 'is_staff')
    list_display_links = ('full_name_display',)
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('id',)
    readonly_fields = ('last_login', 'date_joined')
    add_form = UserCreationForm

    fieldsets = (
        (_('Main information'), {
            'fields': ('username', 'password'),
        }),
        (_('Personal information'), {
            'fields': ('first_name', 'last_name', 'email', 'role', 'avatar'),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important times'), {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (_('Add a new user'), {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'role',
                'password1',
                'password2',
                'is_active',
                'is_staff',
            ),
        }),
    )

    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = _('Full name')

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src=\'{}\' style=\'width: 36px; height: 36px; border-radius: 9999px; object-fit: cover;\' />',
                obj.avatar.url
            )
        return '—'
    avatar_preview.short_description = _('Avatar')


admin.site.unregister(Group)