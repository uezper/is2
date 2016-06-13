from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView
from scrunban.settings import base as base_settings
from apps.administracion.models import Project
from apps.proyecto.mixins import ProjectViwMixin, DefaultFormDataMixin
from apps.proyecto.forms import StateForm


class ProjectStateView(ProjectViwMixin, FormView):
    template_name = "proyecto/project_state"
    form_class = StateForm
    pk_url_kwarg = 'project_id'
    section_title = 'Estado'
    left_active = 'Estado'

    def form_valid(self, form, **kwargs):
        p = Project.objects.get(id=self.kwargs['project_id'])
        if p.get_state() == 'Pendiente':
            import datetime
            p.date_start = datetime.datetime.now().date()
            p.date_end = form.cleaned_data['date_end']
            p.save()
        elif p.get_state() == 'Ejecucion':
            p.cancel = True
            p.save()
        return redirect(base_settings.PROJECT_STATE, project_id=(self.kwargs['project_id']))

    def get_context_data(self, **kwargs):
        context = super(ProjectStateView, self).get_context_data(**kwargs)
        context['URL_NAMES'] = base_settings.URL_NAMES
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        context['error_date_null'] = False
        context['error_date_invalid'] = False
        return context
