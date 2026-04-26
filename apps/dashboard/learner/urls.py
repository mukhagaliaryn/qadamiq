from django.urls import path
from .views import dashboard, modules, levels, tasks

app_name = 'learner'

urlpatterns = [
    path('', dashboard.dashboard_view, name='dashboard'),
    path('modules/', modules.modules_view, name='modules'),
    path('modules/<int:module_id>/', modules.module_detail_view, name='module-detail'),
    path('levels/<int:level_id>/', levels.level_detail_view, name='level-detail'),
    path('tasks/<int:task_id>/', tasks.task_detail_view, name='task-detail'),
]
