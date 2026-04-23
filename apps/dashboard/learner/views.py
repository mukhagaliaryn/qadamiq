from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from core.mixins import RoleRequiredMixin


class LearnerDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'app/dashboard/learner/page.html'
    allowed_roles = ['learner']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Learner dashboard'
        return context


learner_dashboard_view = LearnerDashboardView.as_view()
