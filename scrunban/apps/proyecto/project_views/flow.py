import logging
from scrunban.settings import base as base_settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, FormView
from apps.proyecto.mixins import ProjectViwMixin, DefaultFormDataMixin
from apps.proyecto import forms
from apps.proyecto.models import Flow, Project

# Define loggers
stdlogger = logging.getLogger(base_settings.LOGGERS_NAME['proyecto'])

# Define log entries formatters
def formatter(entity, project, action, actor):
    return '{} de {} ha sido {} por {}'.format(entity, project, action, actor)

class FlowListView(ProjectViwMixin, ListView):

    """
    Clase correspondiente a la vista que lista los flujos de un proyecto

    :param model: Modelo que Django utilizara para listar los objetos
    :param context_object_name: Nombre dentro del context que contendra la lista de objetos.
    :param template_name: Nombre del template que sera utilizado
    :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
    :param paginate_by: Nro. maximo de elementos por pagina
    :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
    :param left_active: Nombre de la seccion activa del menu lateral izquierdo

    Esta clase hereda de `ProjectViewMixin` y de `ListViewMixin`
    """
    model = Flow
    context_object_name = 'flow_list'
    template_name = 'proyecto/project_flow_list'
    pk_url_kwarg = 'project_id'
    paginate_by = 10
    section_title = 'Flujos'
    left_active = 'Flujos'


    def get_required_permissions(self):
        """

        Este metodo genera y retorna una lista de los permisos requeridos para que un usuario pueda acceder a una vista.

        Los permisos deben ser las tuplas de dos elementos definidos en `apps.autenticacion.settings`

        :return: Lista de permisos requeridos para acceder a la vista
        """
        from apps.autenticacion.settings import PROJECT_FLUJO_MANAGEMENT

        required = [
            PROJECT_FLUJO_MANAGEMENT
        ]

        return required


    def get_queryset(self):
        """
        Este metodo retorna el queryset que sera guardado dentro de `context['context_object_name']`

        :return: Queryset. Lista que sera guardada dentro del context
        """

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


class FlowCreateView(ProjectViwMixin, DefaultFormDataMixin, FormView):
    """
    Clase correspondiente a la vista que permite crear un Flujo dentro de un proyecto

    :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
    :param template_name: Nombre del template que sera utilizado
    :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
    :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
    :param left_active: Nombre de la seccion activa del menu lateral izquierdo

    Esta clase hereda de `ProjectViewMixin`, `DefaultFormDataMixin` y de `FormView`

    """

    form_class = forms.CreateFlowForm
    template_name = 'proyecto/project_flow_create_edit_delete'
    pk_url_kwarg = 'project_id'
    section_title = 'Crear Flujo'
    left_active = 'Flujos'

    def get_required_permissions(self):
        """

        Este metodo genera y retorna una lista de los permisos requeridos para que un usuario pueda acceder a una vista.

        Los permisos deben ser las tuplas de dos elementos definidos en `apps.autenticacion.settings`

        :return: Lista de permisos requeridos para acceder a la vista
        """
        from apps.autenticacion.settings import PROJECT_FLUJO_MANAGEMENT

        required = [
            PROJECT_FLUJO_MANAGEMENT
        ]

        return required

    def get_default_fields(self):
        """
        Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

        :return: Diccionario con campos por defectos y sus respectivos valores.
        """
        project = self.get_project()
        data = {
            'project': project.id,
        }
        return data

    def get_success_url(self):
        """
        Retorna la url a donde sera redirigido el usuario cuando se haya procesado correctamente un formulario

        :return: Url
        """
        
        project = self.get_project()

        from scrunban.settings.base import PROJECT_FLOW_LIST
        return reverse(PROJECT_FLOW_LIST, args=(project.id,))

    def get_initial(self):
        """
        Valores por defecto de un formulario al ser cargado por primera vez

        :return: Un diccionario conteniendo los valores por defecto de un formulario
        """
        initial = {
            'activities': ''
        }

        return initial

    def form_valid(self, form):
        """
        Metodo que es llamado cuando un formulario enviado por el usuario es valido.

        :param form: Formulario que ha sido ya comprobado y es valido
        :return: HttpResponse
        """
        form.save()
        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):
        """
        Netodo que es llamado cuando un formulario enviado por el usuario es invalido.

        :param form: Formulario invalido con los errores respectivos
        :return: HttpResponse
        """
        context = {
            'form' : form
        }

        print(form)
        return super(FlowCreateView, self).render_to_response(self.get_context_data(**context))
        
class FlowEditView(FlowCreateView):
    """
    Clase correspondiente a la vista que permite editar un Flujo dentro de un proyecto

    :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
    :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']

    Esta clase hereda de `FlowCreateView`

    """

    form_class = forms.EditFlowForm

    flow_url_kwarg = 'flow_id'

    section_title = 'Editar Flujo'


    def get_default_fields(self):
        """
        Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

        :return: Diccionario con campos por defectos y sus respectivos valores.
        """

        from apps.proyecto.models import Flow

        project = self.get_project()
        flow = get_object_or_404(Flow, id=self.kwargs.get(self.flow_url_kwarg))

        data = {
            'project': project.id,
            'old_name': flow.name
        }

        return data

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna el context que sera enviado al template

        :return: Context
        """
        context = super(FlowEditView, self).get_context_data(**kwargs)
        context['edit_form'] = True
        context['flow'] = self.flow

        return context

    def get_initial(self):
        """
        Valores por defecto de un formulario al ser cargado por primera vez

        :return: Un diccionario conteniendo los valores por defecto de un formulario
        """
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


    :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
    :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']

    Esta clase hereda de `FlowEditView`
    """

    form_class = forms.DeleteFlowForm

    section_title = 'Eliminar Flujo'

    def get_default_fields(self):
        """
        Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

        :return: Diccionario con campos por defectos y sus respectivos valores.
        """
        from apps.proyecto.models import Flow

        project = self.get_project()
        flow = get_object_or_404(Flow, id=self.kwargs.get(self.flow_url_kwarg))

        data = {
            'project': project.id,
            'flow': flow.id
        }

        return data

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna el context que sera enviado al template

        :return: Context
        """
        context = super(FlowDeleteView, self).get_context_data(**kwargs)
        context['delete_form'] = True
        context['no_editable'] = True

        return context
