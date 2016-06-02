from django.shortcuts import get_object_or_404
from django.views.generic import ListView, FormView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import HttpResponseRedirect

from apps.proyecto.mixins import ProjectViwMixin, DefaultFormDataMixin
from apps.proyecto import forms
from apps.proyecto.models import Sprint




class SprintListView(ProjectViwMixin, ListView):
    """
       Clase correspondiente a la vista que lista los sprints de un proyecto

       :param model: Modelo que Django utilizara para listar los objetos
       :param context_object_name: Nombre dentro del context que contendra la lista de objetos.
       :param template_name: Nombre del template que sera utilizado
       :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
       :param paginate_by: Nro. maximo de elementos por pagina
       :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
       :param left_active: Nombre de la seccion activa del menu lateral izquierdo

       Esta clase hereda de `ProjectViewMixin` y de `ListViewMixin`
       """
    model = Sprint
    context_object_name = 'sprint_list'
    template_name = 'proyecto/project_sprint_list'
    pk_url_kwarg = 'project_id'
    paginate_by = 10
    section_title = 'Sprints'
    left_active = 'Sprints'

    def get_required_permissions(self):
        """

        Este metodo genera y retorna una lista de los permisos requeridos para que un usuario pueda acceder a una vista.

        Los permisos deben ser las tuplas de dos elementos definidos en `apps.autenticacion.settings`

        :return: Lista de permisos requeridos para acceder a la vista
        """
        from apps.autenticacion.settings import PROJECT_KANBAN_WATCH

        required = [
            PROJECT_KANBAN_WATCH
        ]

        return required

    def get_queryset(self):
        """
            Este metodo retorna el queryset que sera guardado dentro de `context['context_object_name']`

            :return: Queryset. Lista que sera guardada dentro del context
            """
        project = self.get_project()
        return Sprint.sprints.filter(project=project)

class SprintCreateView(ProjectViwMixin, DefaultFormDataMixin, FormView):
    """
        Clase correspondiente a la vista que permite crear un sprint dentro de un proyecto

        :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
        :param template_name: Nombre del template que sera utilizado
        :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
        :param left_active: Nombre de la seccion activa del menu lateral izquierdo

        Esta clase hereda de `ProjectViewMixin`, `DefaultFormDataMixin` y de `FormView`

        """

    form_class = forms.CreateSprintForm
    template_name = 'proyecto/project_sprint_create_edit_delete'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'
    section_title = 'Crear Sprint'
    left_active = 'Sprints'

    def get_required_permissions(self):
        """

        Este metodo genera y retorna una lista de los permisos requeridos para que un usuario pueda acceder a una vista.

        Los permisos deben ser las tuplas de dos elementos definidos en `apps.autenticacion.settings`

        :return: Lista de permisos requeridos para acceder a la vista
        """
        from apps.autenticacion.settings import PROJECT_SPRINT_MANAGEMENT

        required = [
            PROJECT_SPRINT_MANAGEMENT
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
            'capacity': 0,
            'demmand': 0
        }

        return data

    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """
        context = super(SprintCreateView, self).get_context_data(**kwargs)

        context['user_stories'] = []

        project = self.get_project()

        from apps.administracion.models import UserStory, Grained
        from apps.proyecto.models import Team, Activity


        for us in UserStory.objects.filter(project=project):
            grains = Grained.objects.filter(user_story=us)
            do_not = False

            if (UserStory.states[us.state] == 'Finalizado'):
                continue

            us.weight = "{0:.2f}".format(us.get_weight())
            us.available_flows = us.us_type.flows.all()
            for flow_ in us.available_flows:
                flow_.activities = Activity.objects.filter(flow=flow_).order_by('sec')

            if len(grains) != 0:
                for g in grains:
                    if not(g.sprint.state in ['Finalizado', 'Cancelado']):
                        do_not = True
                        break
                    else:
                        flow_ = g.flow
                        flow_.activities = Activity.objects.filter(flow=flow_)
                        flow_.activity = g.activity
                        flow_.no_editable = ''
                        us.flow = flow_
            if not (do_not):
                context['user_stories'].append(us)

        context['dev_list'] = Team.objects.filter(project=project)

        return context

    def get_success_url(self):
        """
            Retorna la url a donde sera redirigido el usuario cuando se haya procesado correctamente un formulario

            :return: Url
            """
        project = self.get_project()

        from scrunban.settings.base import PROJECT_SPRINT_LIST
        return reverse(PROJECT_SPRINT_LIST, args=(project.id,))

    def get_initial(self):
        """
            Valores por defecto de un formulario al ser cargado por primera vez

            :return: Un diccionario conteniendo los valores por defecto de un formulario
            """
        from apps.proyecto.models import Sprint
        project = self.get_project()
        sec = 1
        sprints = Sprint.objects.filter(project=project)

        if sprints.count() != 0:
            sec = sprints.last().sec + 1


        initial = {
            'sec': 'Sprint ' + str(sec),
            'estimated_time': 1,
            'capacity': 0,
            'demmand': 0
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


        return super(SprintCreateView, self).render_to_response(self.get_context_data(**context))



from apps.proyecto.mixins import ValidateSprintState

class SprintEditView(ValidateSprintState, SprintCreateView):
    """
        Clase correspondiente a la vista que permite editar un sprint dentro de un proyecto

        :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
        :param sprint_url_kwarg: Parametro url que contiene el id del sprint

        Esta clase hereda de `ValidateSprintState` y de `SprintCreateView`

        """

    form_class = forms.EditSprintForm
    sprint_url_kwarg = 'sprint_id'
    section_title = 'Editar Sprint'


    def get_default_fields(self):
        """
            Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

            :return: Diccionario con campos por defectos y sus respectivos valores.
            """
        from apps.proyecto.models import Sprint

        project = self.get_project()
        self.sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg))


        data = {
            'project': project.id,
            'id': self.sprint.id,
            'capacity': 0,
            'demmand': 0
        }

        return data

    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """
        context = super(SprintEditView, self).get_context_data(**kwargs)


        context['edit_form'] = True
        context['sprint'] = self.sprint

        from apps.administracion.models import Grained
        from apps.proyecto.models import Activity




        for g in Grained.objects.filter(sprint=self.sprint):
            if (g.user_story.state != 2):
                temp_ = g.user_story

                temp_.available_flows = g.user_story.us_type.flows.all()

                for flow_ in temp_.available_flows:
                    flow_.activities = Activity.objects.filter(flow=flow_).order_by('sec')

                temp_.weight = "{0:.2f}".format(temp_.get_weight())
                temp_.flow = g.flow
                temp_.flow.activity = g.activity
                temp_.flow.activities = Activity.objects.filter(flow=g.flow).order_by('sec')


                context['user_stories'].append(temp_)



        return context

    def get_initial(self):
        """
            Valores por defecto de un formulario al ser cargado por primera vez

            :return: Un diccionario conteniendo los valores por defecto de un formulario
            """
        from apps.proyecto.models import Sprint
        from apps.administracion.models import Grained

        self.sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg))

        sb = []
        for grain in Grained.objects.filter(sprint=self.sprint):
            if grain.user_story.state != 2:
                us_id = grain.user_story.id
                us_devs = '_'.join([str(g.id) for g in grain.developers.all()])
                sb.append(str(us_id) + ':' + us_devs)

        sb_string = ','.join(sb)

        initial = {
            'sec': 'Sprint ' + str(self.sprint.sec),
            'estimated_time': self.sprint.get_estimated_time(),
            'sprint_backlog': sb_string
        }

        return initial

class SprintDeleteView(SprintEditView):
    """
        Clase correspondiente a la vista que permite eliminar un sprint dentro de un proyecto


        :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']

        Esta clase hereda de `SprintEditView`
        """

    form_class = forms.DeleteSprintForm

    section_title = 'Eliminar Sprint'


    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """
        context = super(SprintDeleteView, self).get_context_data(**kwargs)
        context['delete_form'] = True
        context['no_editable'] = True
        context['sprint'] = self.sprint

        return context



class SprintDetailView(ProjectViwMixin, FormView):
    """
        Clase correspondiente a la vista que muestra los detalles de un sprint de un proyecto

        :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
        :param template_name: Nombre del template que sera utilizado
        :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
        :param user_story_paginate_by: Nro. maximo de user stories por pagina
        :param dev_paginate_by: Nro. maximo de desarrolladores por pagina
        :param us_page_name: Nombre del parametro url que tendra el nro. de pagina actual de user stories
        :param dev_page_name: Nombre del parametro url que tendra el nro. de pagina actual de desarrolladores
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
        :param left_active: Nombre de la seccion activa del menu lateral izquierdo

        Esta clase hereda de `ProjectViewMixin` y de `FormView`
        """

    form_class = forms.ChangeSprintStateForm
    template_name = 'proyecto/project_sprint_detail_view'
    pk_url_kwarg = 'project_id'
    sprint_url_kwarg = 'sprint_id'
    user_story_paginate_by = 10
    dev_paginate_by = 10
    section_title = 'Detalles del Sprint'
    left_active = 'Sprints'
    us_page_name = 'sb_page'
    dev_page_name = 'dev_page'


    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """
        from datetime import timedelta, datetime

        context = super(SprintDetailView, self).get_context_data(**kwargs)
        self.sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg, ''))

        ejecutando = Sprint.objects.filter(project=self.get_project(), state='Ejecucion')
        if len(ejecutando) == 0:
            context['can_execute'] = True

        context['sprint'] = self.sprint
        d_ = self.sprint.start_date

        if d_ != None:
            tzinfo = d_.tzinfo
            now = datetime.now(tzinfo)
            if (self.sprint.state == 'Ejecucion'):
                context['sprint'].start_date = d_
                context['sprint'].progress = '{0:.0f}'.format(((now - d_).seconds / (self.sprint.estimated_time * 3600 * 24)) * 100)
                temp_ = (d_ + timedelta(days=self.sprint.estimated_time) - now)

                if temp_.days > 0:
                    if temp_.days == 1:
                        context['sprint'].faltante = '1 dia'
                    else:
                        context['sprint'].faltante = str(temp_.days) + ' dias'
                elif temp_.seconds > 3600:
                    context['sprint'].faltante = '{0:.0f}'.format((temp_.seconds / 3600)) + ' horas'
                elif temp_.seconds > 60:
                    context['sprint'].faltante = '{0:.0f}'.format((temp_.seconds / 60)) + ' minutos'
                else:
                    context['sprint'].faltante = str(temp_.seconds) + ' segundos'

            elif (self.sprint.state == 'Cancelado'):
                context['sprint'].start_date = d_
                temp_ = (d_ + timedelta(days=self.sprint.estimated_time) - self.sprint.cancel_date)
                if temp_.days > 0:
                    if temp_.days == 1:
                        context['sprint'].faltante = '1 dia'
                    else:
                        context['sprint'].faltante = str(temp_.days) + ' dias'
                elif temp_.seconds > 3600:
                    context['sprint'].faltante = '{0:.0f}'.format((temp_.seconds / 3600)) + ' horas'
                elif temp_.seconds > 60:
                    context['sprint'].faltante = '{0:.0f}'.format((temp_.seconds / 60)) + ' minutos'
                else:
                    context['sprint'].faltante = str(temp_.seconds) + ' segundos'


                context['sprint'].progress = '{0:.0f}'.format(((self.sprint.cancel_date - d_).seconds / (self.sprint.estimated_time * 3600 * 24)) * 100)

        else:
            context['sprint'].start_date = ''
        context['sprint_data'] = self.get_context_sprint_data()

        return context

    def get_context_sprint_data(self):
        """
        Metodo que agrega informacion adicional al context

        :return: Diccionario con datos adicionales
        """
        from apps.administracion.models import Grained

        sprint = self.sprint

        capacity = 0
        demmand = 0

        user_stories = []
        devs = []

        str_states = ['To do', 'Doing', 'Done']
        # Obtiene los desarrolladores del Sprint, sus user stories, su capacidad y su demanda
        for grain in Grained.objects.filter(sprint=sprint):
            temp_ = grain.user_story
            temp_.flow = grain.flow
            temp_.activity = grain.activity
            temp_.state = str_states[grain.state - 1]
            user_stories.append((temp_, grain.developers.all()))
            demmand += grain.user_story.estimated_time

            for dev in grain.developers.all():
                if not(dev in devs):
                    devs.append(dev)
                    capacity += dev.hs_hombre * sprint.estimated_time

        # Paginacion

        us_paginator = Paginator(user_stories, self.user_story_paginate_by)
        us_page = self.request.GET.get(self.us_page_name, 1)
        try:
            user_stories_paginated = us_paginator.page(us_page)
        except PageNotAnInteger:
            user_stories_paginated = us_paginator.page(1)
        except EmptyPage:
            user_stories_paginated = us_paginator.page(us_paginator.num_pages)

        dev_paginator = Paginator(devs, self.dev_paginate_by)
        dev_page = self.request.GET.get(self.dev_page_name, 1)
        try:
            dev_paginated = dev_paginator.page(dev_page)
        except PageNotAnInteger:
            dev_paginated = dev_paginator.page(1)
        except EmptyPage:
            dev_paginated = dev_paginator.page(dev_paginator.num_pages)

        # Prepara el context

        sprint_data = {}
        sprint_data['capacity'] = capacity
        sprint_data['demmand'] = demmand
        sprint_data['user_stories_list'] = user_stories_paginated
        sprint_data['dev_list'] = dev_paginated

        return sprint_data

    def form_valid(self, form):
        """
            Metodo que es llamado cuando un formulario enviado por el usuario es valido.

            :param form: Formulario que ha sido ya comprobado y es valido
            :return: HttpResponse
            """
        context = {}
        sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg, ''))

        if (form.cleaned_data['operation'] == 'ejecutar' and sprint.state == 'Pendiente'):
            from datetime import date, timedelta, datetime

            project_date_end = self.get_project().date_end
            today = date.today()
            sprint_end = today + timedelta(days=sprint.estimated_time)

            if (project_date_end - sprint_end).days < 0:
                context['error'] = True
                context['message'] = 'No se puede ejecutar al Sprint pues el tiempo de finalizacion supera al del proyecto. ' \
                                     'Edite el Sprint e intentelo de nuevo.'
            else:
                from apps.administracion.models import Grained

                grains = Grained.objects.filter(sprint=sprint)
                for g in grains:
                    x = g.user_story
                    x.state = 1
                    x.save()

                sprint.start_date = datetime.now()
                sprint.state = 'Ejecucion'
                sprint.save()
                context['message'] = 'El Sprint ha iniciado su ejecucion'
        elif (form.cleaned_data['operation'] == 'cancelar' and sprint.state == 'Ejecucion'):
            from datetime import datetime

            sprint.state = 'Cancelado'
            sprint.cancel_date = datetime.now()
            sprint.save()

            context['message'] = 'El Sprint ha sido cancelado'

        return super(SprintDetailView, self).render_to_response(self.get_context_data(**context))

    def form_invalid(self, form):
        """
            Netodo que es llamado cuando un formulario enviado por el usuario es invalido.

            :param form: Formulario invalido con los errores respectivos
            :return: HttpResponse
            """
        context = {
            'form': form
        }

        return super(SprintDetailView, self).render_to_response(self.get_context_data(**context))

class SprintKanbanView(ProjectViwMixin, DefaultFormDataMixin, FormView):
    """
        Clase correspondiente a la vista que muestra el kanban de un sprint de un proyecto

        :param form_class: Formulario que se encarga de la validacion de los datos ingresados por usuarios
        :param template_name: Nombre del template que sera utilizado
        :param pk_url_kwarg: Nombre del parametro de url que contiene el id del proyecto
        :param sprint_url_kwarg: Nombre del parametro url que contiene el id del sprint
        :param section_title: Titulo de la Seccion, colocado dentro del context['section_title']
        :param left_active: Nombre de la seccion activa del menu lateral izquierdo

        Esta clase hereda de `ProjectViewMixin`, `DefaultFormDataMixin` y de `FormView`
        """
    form_class = forms.KanbanOperation
    template_name = 'proyecto/project_sprint_kanban'
    pk_url_kwarg = 'project_id'
    sprint_url_kwarg = 'sprint_id'
    section_title = ''
    left_active = 'Sprints'

    def get_context_data(self, **kwargs):
        """
            Metodo que retorna el context que sera enviado al template

            :return: Context
            """

        context = super(SprintKanbanView, self).get_context_data(**kwargs)
        self.sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg, ''))

        context['sprint'] = self.sprint
        context['sprint_data'] = self.get_context_sprint_data()

        return context

    def get_context_sprint_data(self):
        """
        Metodo que agrega informacion adicional al context

        :return: Informacion adicional a ser agregado al context
        """
        from apps.administracion.models import Grained, Note, UserStory
        from apps.proyecto.models import Activity

        sprint = self.sprint

        flows_added = []
        flows = {}


        # Agrupa los US de un Sprint por actividad y flujo
        for grain in Grained.objects.filter(sprint=sprint):
            temp_ = grain.user_story
            temp_.us_state = UserStory.states[grain.user_story.state]
            temp_.flow = grain.flow
            temp_.activity = grain.activity
            temp_.state = grain.state
            temp_.demmand = grain.user_story.estimated_time
            temp_.developers = {}

            for dev in grain.developers.all():
                temp_.developers[dev.user.id] = True

            temp_.worked_time = 0

            grains_us = Grained.objects.filter(user_story=grain.user_story)
            for g in grains_us:
                for note in Note.objects.filter(grained=g, aproved=True):
                    temp_.worked_time = temp_.worked_time + note.work_load

            temp_.completed = '{0:.0f}'.format(min((temp_.worked_time / temp_.estimated_time) * 100, 100))


            if (grain.flow.id not in flows_added):
                flows_added.append(grain.flow.id)
                flows[grain.flow.id] = {}
                flows[grain.flow.id]['flow'] = grain.flow
                flows[grain.flow.id]['activity_list'] = {}

                activity_list = Activity.objects.filter(flow = grain.flow).order_by('sec')
                for act in activity_list:
                    act.states = {
                        '1': [],
                        '2': [],
                        '3': []
                    }
                    flows[grain.flow.id]['activity_list'][act.id] = act


            flows[temp_.flow.id]['activity_list'][temp_.activity.id].states[str(grain.state)].append(temp_)

        flow_list = [flows[id] for id in flows.keys()]
        for flow in flow_list:
            flow['activities'] = []
            for act_id in flow['activity_list']:
                act_ = flow['activity_list'][act_id]
                states_ = [act_.states['1'], act_.states['2'], act_.states['3']]
                act_.states = states_

                flow['activities'].append(act_)

        # Prepara el context

        sprint_data = {}
        sprint_data['flow_list'] = flow_list

        return sprint_data

    def get_default_fields(self):
        """
            Campos por defecto que son agregados a los datos proveidos por los usuarios al enviar un formulario.

            :return: Diccionario con campos por defectos y sus respectivos valores.
            """

        sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg))
        user = self.request.user.user

        data = {
            'grain': sprint.id,
            'user': user.id
        }

        return data

    def form_valid(self, form):
        """
            Metodo que es llamado cuando un formulario enviado por el usuario es valido.

            :param form: Formulario que ha sido ya comprobado y es valido
            :return: HttpResponse
            """
        form.save()
        context = {}
        return super(SprintKanbanView, self).render_to_response(self.get_context_data(**context))

    def form_invalid(self, form):
        """
            Netodo que es llamado cuando un formulario enviado por el usuario es invalido.

            :param form: Formulario invalido con los errores respectivos
            :return: HttpResponse
            """
        context = {
            'form': form
        }
        return super(SprintKanbanView, self).render_to_response(self.get_context_data(**context))
