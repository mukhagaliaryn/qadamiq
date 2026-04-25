from django.shortcuts import render, redirect
from apps.main.views.auth import get_post_auth_redirect_url


# home page
# ----------------------------------------------------------------------------------------------------------------------
def home_view(request):
    if request.user.is_authenticated:
        return redirect(get_post_auth_redirect_url(request.user))

    return render(request, 'app/page.html', {})