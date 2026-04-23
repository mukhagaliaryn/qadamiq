from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_not_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from core.forms.account import LoginForm, RegisterForm


def get_post_auth_redirect_url(user):
    if user.is_superuser or user.is_staff or user.is_admin():
        return reverse('admin:index')

    if user.is_teacher():
        return reverse('teacher:dashboard')

    return reverse('learner:dashboard')


# login page
# ----------------------------------------------------------------------------------------------------------------------
@login_not_required
@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(get_post_auth_redirect_url(request.user))

    form = LoginForm(request=request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, _('Welcome back!'))
        return redirect(get_post_auth_redirect_url(user))

    return render(request, 'app/auth/login/page.html', {
        'form': form,
    })


# register page
# ----------------------------------------------------------------------------------------------------------------------
@login_not_required
@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(get_post_auth_redirect_url(request.user))

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, _('Your account has been created successfully.'))
        return redirect('learner:dashboard')

    return render(request, 'app/auth/register/page.html', {
        'form': form,
    })

# logout action
# ----------------------------------------------------------------------------------------------------------------------
@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    messages.success(request, _('You have been logged out.'))
    return redirect('main:home')


def post_auth_redirect_view(request):
    if not request.user.is_authenticated:
        raise Http404

    return HttpResponseRedirect(get_post_auth_redirect_url(request.user))