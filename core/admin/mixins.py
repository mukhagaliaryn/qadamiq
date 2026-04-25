from django.urls import reverse
from django.utils.html import format_html


class LinkedAdminMixin:
    admin_site_name = 'admin'

    def admin_link(self, obj, label=None, new_tab=False):
        if not obj or not getattr(obj, 'pk', None):
            return '-'

        try:
            url = reverse(
                f'{self.admin_site_name}:{obj._meta.app_label}_{obj._meta.model_name}_change',
                args=[obj.pk],
            )
            target = ' target="_blank"' if new_tab else ''
            text = label or str(obj)

            return format_html(
                '<a href="{}"{} style="color:#4f46e5;font-weight:600;">{}</a>',
                url,
                target,
                text,
            )
        except Exception:
            return '-'

    def parent_link(self, obj, parent_field_name: str, label_field='__str__', new_tab=False):
        parent = getattr(obj, parent_field_name, None)

        if not parent or not getattr(parent, 'pk', None):
            return '-'

        try:
            url = reverse(
                f'{self.admin_site_name}:{parent._meta.app_label}_{parent._meta.model_name}_change',
                args=[parent.pk],
            )

            if label_field == '__str__':
                label = str(parent)
            else:
                label = getattr(parent, label_field, str(parent))

            target = ' target="_blank"' if new_tab else ''

            return format_html(
                '<a href="{}"{} style="color:#4f46e5;font-weight:600;">{}</a>',
                url,
                target,
                label,
            )
        except Exception:
            return '-'
