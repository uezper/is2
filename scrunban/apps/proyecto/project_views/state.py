import logging
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.edit import FormView
from scrunban.settings import base as base_settings
from apps.administracion.models import Project
from apps.proyecto.mixins import ProjectViwMixin
from apps.proyecto.forms import StateForm


# Define loggers
stdlogger = logging.getLogger(base_settings.LOGGERS_NAME['proyecto'])


# Define log entries formatters
def formatter(entity, project, action, actor):
    return '{} de {} ha sido {} por {}'.format(entity, project, action, actor)


class ProjectStateView(ProjectViwMixin, FormView):
    """
    Clase correspondiente a la vista que permite modificar el estado de un proyecto

    :param template_name: Nombre del template que sera utilizado
    :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
    :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
    :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
    :param left_active: Nombre de la seccion activa del menu lateral izquierdo

    Esta clase hereda de `ProjectViewMixin` y de `FormView`
    """
    template_name = "proyecto/project_state"
    form_class = StateForm
    pk_url_kwarg = 'project_id'
    section_title = 'Estado'
    left_active = 'Estado'

    def form_valid(self, form, **kwargs):
        """
        Metodo que es llamado cuando un formulario enviado por el usuario es valido.

        :param form: Formulario que ha sido ya comprobado y es valido
        :return: HttpResponse
        """


        p = Project.objects.get(id=self.kwargs['project_id'])
        if p.get_state() == 'Pendiente':
            import datetime
            p.date_start = datetime.datetime.now().date()
            p.date_end = form.cleaned_data['date_end']
            p.save()
            # Log event
            kwargs = {
                'entity': 'Proyecto',
                'project': self.get_project().name,
                'action': 'cambiado al estado de ejecucion',
                'actor': self.request.user.get_full_name()
            }
            stdlogger.info(formatter(**kwargs))
        elif p.get_state() == 'Ejecucion':
            p.cancel = True
            p.save()
            # Log event
            kwargs = {
                'entity': 'Proyecto',
                'project': self.get_project().name,
                'action': 'cambiado al estado cancelado',
                'actor': self.request.user.get_full_name()
            }
            stdlogger.info(formatter(**kwargs))
        return redirect(base_settings.PROJECT_STATE, project_id=(self.kwargs['project_id']))

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna el context que sera enviado al template

        :return: Context
        """
        context = super(ProjectStateView, self).get_context_data(**kwargs)
        context['URL_NAMES'] = base_settings.URL_NAMES
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        context['error_date_null'] = False
        context['error_date_invalid'] = False
        return context
