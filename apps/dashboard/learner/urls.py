from django.urls import path
from apps.dashboard.learner import views

app_name = 'learner'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('modules/', views.modules_view, name='modules'),
    path('progress/', views.progress_view, name='progress'),
]
