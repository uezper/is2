from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, FormView
from apps.proyecto.mixins import ProjectViwMixin, DefaultFormData
from apps.proyecto import forms
from apps.proyecto.models import Flow

class FlowListView(ProjectViwMixin, ListView):

    """
    Clase correspondiente a la vista que lista los flujos de un proyecto


    """
    model = Flow
    context_object_name = 'flow_list'
    template_name = 'proyecto/project_flow_list'
    pk_url_kwarg = 'project_id'
    paginate_by = 10
    section_title = 'Flujos'
    left_active = 'Flujos'

    def get_queryset(self):
        from apps.administracion.models import UserStoryType, Grained
        from apps.proyecto.models import Sprint

        project = self.get_project()

        flows = Flow.objects.filter(project=project)
        for f in flows:
            f.can_delete = True
            f.can_edit = True

            for ust in UserStoryType.objects.filter(project=project):
                if f in ust.flows.all():
                    f.can_delete = False
            for s in Sprint.objects.filter(project=project):
                for g in Grained.objects.filter(sprint=s):
                    if f in g.user_story.us_type.flows.all():
                        f.can_edit = False

        return flows


class FlowCreateView(ProjectViwMixin, DefaultFormData, FormView):
    """
    Clase correspondiente a la vista que permite crear un Flujo dentro de un proyecto

    """

    form_class = forms.CreateFlowForm
    template_name = 'proyecto/project_flow_create_edit_delete'
    pk_url_kwarg = 'project_id'
    section_title = 'Crear Flujo'
    left_active = 'Flujos'

    def get_default_fields(self):
        project = self.get_project()
        data = {
            'project': project.id,
        }
        return data

    def get_success_url(self):
        project = self.get_project()

        from scrunban.settings.base import PROJECT_FLOW_LIST
        return reverse(PROJECT_FLOW_LIST, args=(project.id,))

    def get_initial(self):
        initial = {
            'activities': ''
        }

        return initial

    def form_valid(self, form):

        form.save()
        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):

        context = {
            'form' : form
        }

        print(form)
        return super(FlowCreateView, self).render_to_response(self.get_context_data(**context))


class FlowEditView(FlowCreateView):
    """
    Clase correspondiente a la vista que permite editar un Flujo dentro de un proyecto

    """

    form_class = forms.EditFlowForm

    flow_url_kwarg = 'flow_id'

    section_title = 'Editar Flujo'


    def get_default_fields(self):
        from apps.proyecto.models import Flow

        project = self.get_project()
        flow = get_object_or_404(Flow, id=self.kwargs.get(self.flow_url_kwarg))

        data = {
            'project': project.id,
            'old_name': flow.name
        }

        return data

    def get_context_data(self, **kwargs):
        context = super(FlowEditView, self).get_context_data(**kwargs)
        context['edit_form'] = True
        context['flow'] = self.flow

        return context

    def get_initial(self):
        from apps.proyecto.models import Flow, Activity

        self.flow = get_object_or_404(Flow, id=self.kwargs.get(self.flow_url_kwarg))

        initial = {
            'name': self.flow.name,
            'activities': ','.join([ac.name for ac in Activity.objects.filter(flow=self.flow)])
        }

        return initial

class FlowDeleteView(FlowEditView):
    """
    Clase correspondiente a la vista que permite eliminar un Flujo dentro de un proyecto

    """

    form_class = forms.DeleteFlowForm

    section_title = 'Eliminar Flujo'

    def get_default_fields(self):
        from apps.proyecto.models import Flow

        project = self.get_project()
        flow = get_object_or_404(Flow, id=self.kwargs.get(self.flow_url_kwarg))

        data = {
            'project': project.id,
            'flow': flow.id
        }

        return data

    def get_context_data(self, **kwargs):
        context = super(FlowDeleteView, self).get_context_data(**kwargs)
        context['delete_form'] = True
        context['no_editable'] = True

        return context
