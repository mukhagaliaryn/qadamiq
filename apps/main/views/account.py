from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from core.forms.account import DeleteAccountForm, PasswordChangeCustomForm, ProfileForm


# profile page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def profile_view(request):
    return render(request, 'app/account/profile/page.html', {
        'user_profile': request.user,
    })


# profile edit page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
@require_http_methods(['GET', 'POST'])
def profile_edit_view(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Profile updated successfully.'))
        return redirect('main:profile')

    return render(request, 'app/account/edit/page.html', {
        'form': form,
    })


# settings page
# ---------------------------------------------------------------------------------------------------------------------
@login_required
@require_http_methods(['GET', 'POST'])
def settings_view(request):
    password_form = PasswordChangeCustomForm(request.user)
    delete_form = DeleteAccountForm(request.user, prefix='delete')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_password':
            password_form = PasswordChangeCustomForm(request.user, request.POST)
            delete_form = DeleteAccountForm(request.user, prefix='delete')

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Password changed successfully.'))
                return redirect('main:settings')

        if action == 'delete_account':
            password_form = PasswordChangeCustomForm(request.user)
            delete_form = DeleteAccountForm(request.user, request.POST, prefix='delete')

            if delete_form.is_valid():
                user = request.user
                logout(request)
                user.delete()
                messages.success(request, _('Account deleted successfully.'))
                return redirect('main:home')

    return render(request, 'app/account/settings/page.html', {
        'password_form': password_form,
        'delete_form': delete_form,
    })
