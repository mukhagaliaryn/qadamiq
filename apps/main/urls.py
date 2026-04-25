from django.urls import path
from .views import home, auth, account

app_name = 'main'

urlpatterns = [
    path('', home.home_view, name='home'),

    # auth views...
    path('auth/login/', auth.login_view, name='login'),
    path('auth/register/', auth.register_view, name='register'),
    path('auth/logout/', auth.logout_view, name='logout'),

    # account views...
    path('account/profile/', account.profile_view, name='profile'),
    path('account/profile/edit/', account.profile_edit_view, name='profile-edit'),
    path('account/settings/', account.settings_view, name='settings'),
]
