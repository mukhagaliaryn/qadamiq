from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from core.mixins import RoleRequiredMixin


class TeacherDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'app/dashboard/teacher/page.html'
    allowed_roles = ['teacher']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Teacher dashboard'
        return context


teacher_dashboard_view = TeacherDashboardView.as_view()
