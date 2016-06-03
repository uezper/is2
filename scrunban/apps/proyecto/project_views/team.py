from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, FormView
from apps.proyecto.mixins import ProjectViwMixin, DefaultFormDataMixin
from apps.proyecto import forms
from apps.proyecto.models import Team

class DevListView(ProjectViwMixin, ListView):
    """
        Clase correspondiente a la vista que lista los desarrolladores de un proyecto

        :param model: Modelo que Django utilizara para listar los objetos
        :param context_object_name: Nombre dentro del context que contendra la lista de objetos.
        :param template_name: Nombre del template que sera utilizado
        :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
        :param paginate_by: Nro. maximo de elementos por pagina
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
        :param left_active: Nombre de la seccion activa del menu lateral izquierdo

        Esta clase hereda de `ProjectViewMixin` y de `ListViewMixin`
        """
    model = Team
    context_object_name = 'dev_list'
    template_name = 'proyecto/project_dev_team_list'
    pk_url_kwarg = 'project_id'
    paginate_by = 10
    section_title = 'Equipo de Desarrollo'
    left_active = 'Equipo de Desarrollo'

    def get_required_permissions(self):
        """

        Este metodo genera y retorna una lista de los permisos requeridos para que un usuario pueda acceder a una vista.

        Los permisos deben ser las tuplas de dos elementos definidos en `apps.autenticacion.settings`

        :return: Lista de permisos requeridos para acceder a la vista
        """
        from apps.autenticacion.settings import PROJECT_DEV_MANAGEMENT

        required = [
            PROJECT_DEV_MANAGEMENT
        ]

        return required

    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """
        context = super(DevListView, self).get_context_data(**kwargs)
        cap = 0
        for t in Team.objects.filter(project=self.get_project()):
            cap = cap + t.hs_hombre

        context['capacity'] = cap
        return context

    def get_queryset(self):
        """
            Este metodo retorna el queryset que sera guardado dentro de `context['context_object_name']`

            :return: Queryset. Lista que sera guardada dentro del context
            """
        project = self.get_project()
        return Team.teams.filter(project=project)



class DevEditView(ProjectViwMixin, DefaultFormDataMixin, FormView):
    """
       Clase correspondiente a la vista que permite editar la cantidad de hs-hombre de un desarrollador dentro de un proyecto

       :param context_object_name: Nombre dentro del context que contendra la lista de objetos.
       :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
       :param template_name: Nombre del template que sera utilizado
       :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
       :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
       :param left_active: Nombre de la seccion activa del menu lateral izquierdo

       Esta clase hereda de `ProjectViewMixin`, `DefaultFormDataMixin` y de `FormView`

       """

    form_class = forms.EditDevForm

    section_title = 'Editar Cantidad de Horas Hombre'
    team_id_kwname = 'team_id'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'
    template_name = 'proyecto/project_dev_team_edit'
    left_active = 'Equipo de Desarrollo'

    def get_required_permissions(self):
        """

        Este metodo genera y retorna una lista de los permisos requeridos para que un usuario pueda acceder a una vista.

        Los permisos deben ser las tuplas de dos elementos definidos en `apps.autenticacion.settings`

        :return: Lista de permisos requeridos para acceder a la vista
        """
        from apps.autenticacion.settings import PROJECT_DEV_MANAGEMENT

        required = [
            PROJECT_DEV_MANAGEMENT
        ]

        return required

    def get_initial(self):
        """
            Valores por defecto de un formulario al ser cargado por primera vez

            :return: Un diccionario conteniendo los valores por defecto de un formulario
            """
        team_id = self.kwargs.get(self.team_id_kwname)
        team = get_object_or_404(Team, id=team_id)

        initial = {
            'id': team.id,
            'username': team.user.get_first_name() + ' ' + team.user.get_last_name(),
            'hs_hombre': team.hs_hombre
        }


        return initial

    def get_default_fields(self):
        """
            Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

            :return: Diccionario con campos por defectos y sus respectivos valores.
            """
        team = get_object_or_404(Team, id=self.kwargs.get(self.team_id_kwname))

        data = {
            'id': team.id,
        }
        return data

    def get_success_url(self):
        """
            Retorna la url a donde sera redirigido el usuario cuando se haya procesado correctamente un formulario

            :return: Url
            """
        project = self.get_project()

        from scrunban.settings.base import PROJECT_DEV_LIST
        return reverse(PROJECT_DEV_LIST, args=(project.id,))


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
            'form': form
        }
        print(form)

        return super(DevEditView, self).render_to_response(self.get_context_data(**context))


