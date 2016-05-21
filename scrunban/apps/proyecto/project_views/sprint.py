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
        from apps.proyecto.models import Team

        for us in UserStory.objects.filter(project=project):
            grains = Grained.objects.filter(user_story=us)
            do_not = False
            us.flow_list = us.us_type.flows.all()
            if len(grains) != 0:
                for g in grains:
                    if g.sprint.state != 'Finalizado':
                        do_not = True
                        break
                    else:
                        us.flow_list = [g.flow]
            if not (do_not):
                context['user_stories'].append((us, us.get_weight()))

        context['user_stories'].sort(key=lambda x: -x[1])
        temp = [ (x[0], "{0:.2f}".format(x[1])) for x in context['user_stories'] ]
        context['user_stories'] = temp
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

        print(form)
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

        project = self.get_project()

        from apps.administracion.models import Grained, UserStory

        context['user_stories'] = []
        for us in UserStory.objects.filter(project=project):
            grains = Grained.objects.filter(user_story=us)
            do_not = False
            us.flow_list = us.us_type.flows.all()
            if len(grains) != 0:
                for g in grains:
                    if g.sprint.state != 'Finalizado':
                        do_not = True
                        break
                    else:
                        us.flow_list = g.flow
            if not(do_not):
                context['user_stories'].append((us, us.get_weight()))

        for g in Grained.objects.filter(sprint=self.sprint):
            temp_ = g.user_story
            temp_.flow_list = [g.flow]
            context['user_stories'].append((temp_, g.user_story.get_weight()))

        context['user_stories'].sort(key=lambda x: -x[1])

        temp = [(x[0], "{0:.2f}".format(x[1])) for x in context['user_stories']]
        context['user_stories'] = temp

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



class SprintDetailView(ProjectViwMixin, TemplateView):

    """
    Clase correspondiente a la vista que muestra la informacion sobre un Sprint de un proyecto

    """

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
        context = super(SprintDetailView, self).get_context_data(**kwargs)

        self.sprint = get_object_or_404(Sprint, id=kwargs.get(self.sprint_url_kwarg, ''))

        context['sprint'] = self.sprint
        context['sprint_data'] = self.get_context_sprint_data()

        return context

    def get_context_sprint_data(self):
        from apps.administracion.models import Grained

        sprint = self.sprint

        capacity = 0
        demmand = 0

        user_stories = []
        devs = []

        # Obtiene los desarrolladores del Sprint, sus user stories, su capacidad y su demanda
        for grain in Grained.objects.filter(sprint=sprint):
            temp_ = grain.user_story
            temp_.flow = grain.flow
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


