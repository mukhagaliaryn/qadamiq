from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# LoginForm
# ----------------------------------------------------------------------------------------------------------------------
class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label=_('Имя пользователя или адрес электронной почты'),
        max_length=150
    )
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput
    )

    error_messages = {
        'invalid_login': _('Пожалуйста, введите правильное имя пользователя/адрес электронной почты и пароль.'),
        'inactive': _('Эта учетная запись неактивна.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_username_or_email(self):
        value = self.cleaned_data['username_or_email'].strip()
        return value

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username_or_email and password:
            user = self._authenticate_user(username_or_email, password)
            if user is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login'
                )
            if not user.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive'
                )
            self.user_cache = user

        return cleaned_data

    def _authenticate_user(self, username_or_email, password):
        user = authenticate(
            self.request,
            username=username_or_email,
            password=password
        )
        if user is not None:
            return user

        matched_user = User.objects.filter(email__iexact=username_or_email).first()
        if not matched_user:
            return None

        return authenticate(
            self.request,
            username=matched_user.username,
            password=password
        )

    def get_user(self):
        return self.user_cache


# RegisterForm
# ----------------------------------------------------------------------------------------------------------------------
class RegisterForm(UserCreationForm):
    email = forms.EmailField(label=_('Электронная почта'))
    first_name = forms.CharField(label=_('Имя'), max_length=150)
    last_name = forms.CharField(label=_('Фамилия'), max_length=150)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('Пользователь с таким адресом электронной почты уже существует.'))
        return email

    def _build_unique_username(self, email):
        base_username = email.split('@')[0].strip().lower()
        base_username = base_username.replace(' ', '')

        if not base_username:
            base_username = 'user'

        candidate = base_username
        counter = 1

        while User.objects.filter(username=candidate).exists():
            counter += 1
            candidate = f'{base_username}{counter}'

        return candidate

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].strip().lower()

        user.email = email
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        user.username = self._build_unique_username(email)
        user.role = User.Role.LEARNER

        if commit:
            user.save()

        return user


# ProfileForm
# ----------------------------------------------------------------------------------------------------------------------
class ProfileForm(forms.ModelForm):
    remove_avatar = forms.BooleanField(
        label=_('Удалить аватар'),
        required=False
    )

    class Meta:
        model = User
        fields = (
            'avatar',
            'username',
            'email',
            'first_name',
            'last_name',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('Пользователь с таким адресом электронной почты уже существует.'))
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('Пользователь с таким именем пользователя уже существует.'))
        return username

    def save(self, commit=True):
        remove_avatar = self.cleaned_data.get('remove_avatar', False)

        if remove_avatar and self.instance.avatar:
            self.instance.avatar = None

        return super().save(commit=commit)


# PasswordChangeCustomForm
# ----------------------------------------------------------------------------------------------------------------------
class PasswordChangeCustomForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_('Текущий пароль'),
        strip=False,
        widget=forms.PasswordInput
    )
    new_password1 = forms.CharField(
        label=_('Новый пароль'),
        strip=False,
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label=_('Подтвердите новый пароль'),
        strip=False,
        widget=forms.PasswordInput
    )


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput
    )
    confirm = forms.BooleanField(
        label=_('Я понимаю, что это действие не может быть отменено.'),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(_('Неверный пароль.'))
        return password


# LanguageSettingsForm
# ----------------------------------------------------------------------------------------------------------------------
class LanguageSettingsForm(forms.Form):
    language = forms.ChoiceField(
        label=_('Language'),
        choices=(
            ('en', _('English')),
            ('ru', _('Russian')),
            ('kk', _('Kazakh')),
        )
    )
