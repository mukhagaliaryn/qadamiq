from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UFModelAdmin
from unfold.forms import UserCreationForm, AdminPasswordChangeForm
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
    readonly_fields = ('last_login', 'date_joined', 'password_change_link')
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('username', 'password', 'password_change_link'),
        }),
        (_('Личная информация'), {
            'fields': ('first_name', 'last_name', 'email', 'role', 'avatar'),
        }),
        (_('Разрешения'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Входы'), {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (_('Добавить нового пользователя'), {
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
    full_name_display.short_description = _('Полное имя')

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src=\'{}\' style=\'width: 36px; height: 36px; border-radius: 9999px; object-fit: cover;\' />',
                obj.avatar.url
            )
        return format_html(
            '<img src=\'{}\' style=\'width: 36px; height: 36px; border-radius: 9999px; object-fit: cover;\' />',
            '/static/images/user-avatar.png'
        )
    avatar_preview.short_description = _('Аватар')

    def password_change_link(self, obj):
        if not obj or not obj.pk:
            return '-'

        return format_html(
            '<a href="../password/" style="font-weight:600;color: #4f46e5;">{}</a>',
            _('Изменить пароль'),
        )
    password_change_link.short_description = _('Смена пароля')


admin.site.unregister(Group)
