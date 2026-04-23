from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from core.forms.account import (
    DeleteAccountForm,
    LanguageSettingsForm,
    PasswordChangeCustomForm,
    ProfileForm,
)


# profile page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@require_http_methods(['GET', 'POST'])
def profile_view(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Your profile has been updated.'))
        return redirect('main:profile')

    return render(request, 'app/account/profile/page.html', {
        'form': form,
        'default_avatar_url': 'images/default-user.png',
    })


# security page
# ---------------------------------------------------------------------------------------------------------------------
@login_required
@require_http_methods(['GET', 'POST'])
def security_view(request):
    password_form = PasswordChangeCustomForm(request.user, request.POST or None)
    delete_form = DeleteAccountForm(request.user, request.POST or None, prefix='delete')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_password':
            password_form = PasswordChangeCustomForm(request.user, request.POST)
            delete_form = DeleteAccountForm(request.user, prefix='delete')

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Your password has been changed.'))
                return redirect('main:security')

        elif action == 'delete_account':
            password_form = PasswordChangeCustomForm(request.user)
            delete_form = DeleteAccountForm(request.user, request.POST, prefix='delete')

            if delete_form.is_valid():
                user = request.user
                logout(request)
                user.delete()
                messages.success(request, _('Your account has been deleted.'))
                return redirect('main:home')

    return render(request, 'app/account/security.html', {
        'password_form': password_form,
        'delete_form': delete_form,
    })


# settings page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@require_http_methods(['GET', 'POST'])
def settings_view(request):
    initial = {
        'language': request.session.get(settings.LANGUAGE_SESSION_KEY, translation.get_language()),
    }
    form = LanguageSettingsForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        language = form.cleaned_data['language']
        request.session[settings.LANGUAGE_SESSION_KEY] = language
        translation.activate(language)

        response = redirect('main:settings')
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        messages.success(request, _('Language settings have been updated.'))
        return response

    return render(request, 'app/account/settings/page.html', {
        'form': form,
    })
