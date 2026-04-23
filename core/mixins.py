from django.http import Http404


class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404

        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        if request.user.role not in self.allowed_roles:
            raise Http404

        return super().dispatch(request, *args, **kwargs)
