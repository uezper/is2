from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, FormView
from apps.proyecto.mixins import ProjectViwMixin, DefaultFormData
from apps.proyecto import forms
from apps.proyecto.models import Team

class DevListView(ProjectViwMixin, ListView):

    """
    Clase correspondiente a la vista que lista los desarrolladores de un proyecto


    """
    model = Team
    context_object_name = 'dev_list'
    template_name = 'proyecto/project_dev_team_list'
    pk_url_kwarg = 'project_id'
    paginate_by = 10
    section_title = 'Equipo de Desarrollo'
    left_active = 'Equipo de Desarrollo'

    def get_context_data(self, **kwargs):
        context = super(DevListView, self).get_context_data(**kwargs)
        cap = 0
        for t in Team.objects.filter(project=self.get_project()):
            cap = cap + t.hs_hombre

        context['capacity'] = cap
        return context

    def get_queryset(self):
        project = self.get_project()
        return Team.teams.filter(project=project)



class DevEditView(ProjectViwMixin, DefaultFormData, FormView):
    """
    Clase correspondiente a la vista que permite editar la cantidad de hs-hombre de un usuario dentro de un proyecto

    """

    form_class = forms.EditDevForm

    section_title = 'Editar Cantidad de Horas Hombre'
    team_id_kwname = 'team_id'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'
    template_name = 'proyecto/project_dev_team_edit'
    left_active = 'Equipo de Desarrollo'

    def get_initial(self):
        team_id = self.kwargs.get(self.team_id_kwname)
        team = get_object_or_404(Team, id=team_id)

        initial = {
            'id': team.id,
            'username': team.user.get_first_name() + ' ' + team.user.get_last_name(),
            'hs_hombre': team.hs_hombre
        }


        return initial

    def get_default_fields(self):
        team = get_object_or_404(Team, id=self.kwargs.get(self.team_id_kwname))

        data = {
            'id': team.id,
        }
        return data

    def get_success_url(self):
        project = self.get_project()

        from scrunban.settings.base import PROJECT_DEV_LIST
        return reverse(PROJECT_DEV_LIST, args=(project.id,))


    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):

        context = {
            'form': form
        }
        print(form)

        return super(DevEditView, self).render_to_response(self.get_context_data(**context))


