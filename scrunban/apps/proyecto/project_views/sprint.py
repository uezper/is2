from django.shortcuts import get_object_or_404
from django.views.generic import ListView, FormView, TemplateView
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import HttpResponseRedirect

from apps.proyecto.mixins import ProjectViwMixin, DefaultFormData
from apps.proyecto import forms
from apps.proyecto.models import Sprint, Project




class SprintListView(ProjectViwMixin, ListView):

    """
    Clase correspondiente a la vista que lista los Sprints de un proyecto

    """
    model = Sprint
    context_object_name = 'sprint_list'
    template_name = 'proyecto/project_sprint_list'
    pk_url_kwarg = 'project_id'
    paginate_by = 10
    section_title = 'Sprints'
    left_active = 'Sprints'

    def get_queryset(self):
        project = self.get_project()
        return Sprint.sprints.filter(project=project)

class SprintCreateView(ProjectViwMixin, DefaultFormData, FormView):
    """
    Clase correspondiente a la vista que permite crear un Sprint dentro de un proyecto

    """

    form_class = forms.CreateSprintForm
    template_name = 'proyecto/project_sprint_create_edit_delete'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'
    section_title = 'Crear Sprint'
    left_active = 'Sprints'

    def get_fail_permission_url(self, request, *args, **kwargs):
        from scrunban.settings.base import PROJECT_INDEX
        return reverse(PROJECT_INDEX, args=(kwargs[self.pk_url_kwarg],))

    def get_required_permissions(self):
        from apps.autenticacion.settings import PROJECT_SPRINT_MANAGEMENT
        from django.contrib.auth.models import Permission

        required = []
        required.append(PROJECT_SPRINT_MANAGEMENT)

        res = [Permission.objects.get(codename=p[0]) for p in required]

        return res

    def get_default_fields(self):
        project = self.get_project()

        data = {
            'project': project.id,
            'capacity': 0,
            'demmand': 0
        }

        return data

    def get_context_data(self, **kwargs):
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
        project = self.get_project()

        from scrunban.settings.base import PROJECT_SPRINT_LIST
        return reverse(PROJECT_SPRINT_LIST, args=(project.id,))

    def get_initial(self):
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

        form.save()
        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):

        context = {
            'form' : form
        }


        return super(SprintCreateView, self).render_to_response(self.get_context_data(**context))



from apps.proyecto.mixins import ValidateSprintStatePending

class SprintEditView(ValidateSprintStatePending, SprintCreateView):
    """
    Clase correspondiente a la vista que permite editar un Sprint dentro de un proyecto

    """

    form_class = forms.EditSprintForm
    sprint_url_kwarg = 'sprint_id'
    section_title = 'Editar Sprint'


    def get_default_fields(self):
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
        context = super(SprintEditView, self).get_context_data(**kwargs)


        context['edit_form'] = True
        context['sprint'] = self.sprint

        from apps.administracion.models import Grained
        from apps.proyecto.models import Activity




        for g in Grained.objects.filter(sprint=self.sprint):
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
        from apps.proyecto.models import Sprint
        from apps.administracion.models import Grained

        self.sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg))

        sb = []
        for grain in Grained.objects.filter(sprint=self.sprint):
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
    Clase correspondiente a la vista que permite eliminar un Sprint dentro de un proyecto

    """

    form_class = forms.DeleteSprintForm

    section_title = 'Eliminar Sprint'


    def get_context_data(self, **kwargs):
        context = super(SprintDeleteView, self).get_context_data(**kwargs)
        context['delete_form'] = True
        context['no_editable'] = True
        context['sprint'] = self.sprint

        return context



class SprintDetailView(ProjectViwMixin, FormView):

    """
    Clase correspondiente a la vista que muestra la informacion sobre un Sprint de un proyecto

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
        from datetime import date, timedelta

        context = super(SprintDetailView, self).get_context_data(**kwargs)
        self.sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg, ''))

        ejecutando = Sprint.objects.filter(project=self.get_project(), state='Ejecucion')
        if len(ejecutando) == 0:
            context['can_execute'] = True

        context['sprint'] = self.sprint
        d_ = self.sprint.start_date
        if d_ != None:
            context['sprint'].start_date = '{}/{}/{}'.format(d_.day, d_.month, d_.year)
            context['sprint'].faltante = (d_ + timedelta(days=self.sprint.estimated_time) - date.today()).days
            context['sprint'].progress = '{0:.0f}'.format(((date.today() - d_).days / self.sprint.estimated_time) * 100)
            print(context['sprint'].progress)
        else:
            context['sprint'].start_date = ''
        context['sprint_data'] = self.get_context_sprint_data()

        return context

    def get_context_sprint_data(self):
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
        context = {}
        sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg, ''))

        if (form.cleaned_data['operation'] == 'ejecutar' and sprint.state == 'Pendiente'):
            from datetime import date, timedelta

            project_date_end = self.get_project().date_end
            today = date.today()
            sprint_end = today + timedelta(days=sprint.estimated_time)

            if (project_date_end - sprint_end).days < 0:
                context['error'] = True
                context['message'] = 'No se puede ejecutar al Sprint pues el tiempo de finalizacion supera al del proyecto. ' \
                                     'Edite el Sprint e intentelo de nuevo.'
            else:

                sprint.start_date = date.today()
                sprint.state = 'Ejecucion'
                sprint.save()
                context['message'] = 'El Sprint ha iniciado su ejecucion'
        elif (form.cleaned_data['operation'] == 'cancelar' and sprint.state == 'Ejecucion'):

            sprint.state = 'Cancelado'
            sprint.save()
            context['message'] = 'El Sprint ha sido cancelado'

        return super(SprintDetailView, self).render_to_response(self.get_context_data(**context))

    def form_invalid(self, form):

        context = {
            'form': form
        }

        return super(SprintDetailView, self).render_to_response(self.get_context_data(**context))

