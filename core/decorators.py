from functools import wraps
from django.http import Http404


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise Http404

            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)

            if request.user.role not in roles:
                raise Http404

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
