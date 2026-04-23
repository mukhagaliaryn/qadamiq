from django.urls import path
from .views import learner_dashboard_view

app_name = 'learner'

urlpatterns = [
    path('', learner_dashboard_view, name='dashboard'),
]