import logging
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .forms import ProjectForm, UserStoryForm, FlowForm, UserStoryTypeForm
from apps.autenticacion.models import User
from apps.autenticacion.decorators import login_required

from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from apps.proyecto.models import Project
from apps.administracion.models import UserStory, UserStoryType, Flow
from apps.administracion import forms

from apps.proyecto.mixins import UrlNamesContextMixin
from apps.autenticacion.mixins import UserPermissionContextMixin, UserIsAuthenticatedMixin

from scrunban.settings import base as base_settings

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES
from django.contrib.auth.models import Permission

# Define loggers
stdlogger = logging.getLogger(base_settings.LOGGERS_NAME['administracion'])

# Define log entries formatters
def formatter(entity, project, action, actor):
    return '{} de {} ha sido {}'.format(entity, project, action)


class ProjectListView(UserIsAuthenticatedMixin, ListView, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite listar los proyectos
    """
    model = Project
    context_object_name = 'project_list'
    template_name = 'administracion/project_list.html'
    allow_empty = True
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        self.get_url_context(context)
        self.get_user_permissions_context(context)
        context['section_title'] = 'Proyectos'
        context['left_active'] = 'Proyectos'
        return context

class ProjectCreateView(UserIsAuthenticatedMixin, CreateView, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite crear un proyecto
    """
    template_name = 'administracion/project_new.html'
    model = Project
    context_object_name = 'project'
    fields = ['name', 'scrum_master', 'product_owner']

    lastForm = forms.ProjectForm()

    def get_success_url(self):
        return reverse(base_settings.ADM_PROJECT_LIST)

    def form_valid(self, form):
        p = form.save()
        # Crea roles por defecto
        for rol in DEFAULT_PROJECT_ROLES:
            role_data = {
                'name': rol[0],
                'desc_larga':  rol[1]
            }
            new_rol = p.add_rol(**role_data)
            for perm_ in rol[2]:
                (perm_[0])
                perm = Permission.objects.get(codename=perm_[0])
                new_rol.add_perm(perm)
        p_id = p.id
        for rol in p.get_roles():
            if rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[0][0]:
                rol.add_user(form.cleaned_data['scrum_master'])
            elif rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[1][0]:
                rol.add_user(form.cleaned_data['product_owner'])
        return HttpResponseRedirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            self.lastForm = forms.ProjectForm(request.POST)
        return super(ProjectCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProjectCreateView, self).get_context_data(**kwargs)
        self.get_url_context(context)
        self.get_user_permissions_context(context)
        context['form'] = self.lastForm

        context['user_list'] = []
        for u in User.objects.all():
            if u.user.is_active:
                context['user_list'].append(u)

        context['section_title'] = 'Crear Proyecto'
        context['left_active'] = 'Proyectos'
        return context


class ProjectModifyView(UserIsAuthenticatedMixin, UpdateView, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite modificar un proyecto
    """
    template_name = 'administracion/project_modify.html'
    model = Project
    context_object_name = 'project'
    fields = ['name', 'scrum_master', 'product_owner']

    def get_success_url(self):
        return reverse(base_settings.ADM_PROJECT_LIST)

    def form_valid(self, form):
        p = Project.objects.get(name=form.cleaned_data['name'])
        p_id = p.id
        # Quita el rol al usuario anterior
        for rol in p.get_roles():
            if rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[0][0]:
                rol.remove_user(p.scrum_master)
            elif rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[1][0]:
                rol.remove_user(p.product_owner)
        # Guarda los cambios
        p = form.save()
        # Asigna el rol al nuevo usuario
        for rol in p.get_roles():
            if rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[0][0]:
                rol.add_user(form.cleaned_data['scrum_master'])
            elif rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[1][0]:
                rol.add_user(form.cleaned_data['product_owner'])
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ProjectModifyView, self).get_context_data(**kwargs)
        self.get_url_context(context)
        self.get_user_permissions_context(context)
        context['user_list'] = []
        for u in User.objects.all():
            if u.user.is_active:
                context['user_list'].append(u)
        context['section_title'] = 'Modificar Proyecto'
        context['left_active'] = 'Proyectos'
        p = Project.objects.get(id=self.kwargs['pk'])
        context['project_state'] = p.get_state
        return context


class ProjectDeleteView(UserIsAuthenticatedMixin, DeleteView, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite eliminar un proyecto
    """
    template_name = 'administracion/project_delete.html'
    model = Project
    context_object_name = 'project'

    def delete(self, *args, **kwargs):
        p = Project.objects.get(id=self.kwargs['pk'])
        p_id = p.id
        # Quita el rol al usuario
        for rol in p.get_roles():
            if rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[0][0]:
                rol.remove_user(p.scrum_master)
            elif rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[1][0]:
                rol.remove_user(p.product_owner)

        return super(ProjectDeleteView, self).delete(*args, **kwargs)

    def get_success_url(self):
        return reverse(base_settings.ADM_PROJECT_LIST)

    def get_context_data(self, **kwargs):
        context = super(ProjectDeleteView, self).get_context_data(**kwargs)
        self.get_url_context(context)
        self.get_user_permissions_context(context)
        context['form'] = forms.ProjectForm(instance=Project.objects.get(id=self.kwargs['pk']))
        context['user_list'] = User.objects.all()
        context['section_title'] = 'Eliminar Proyecto'
        context['left_active'] = 'Proyectos'

        context['project_state'] = Project.objects.get(id=self.kwargs['pk']).get_state()
        return context


class UserCreateView(UserIsAuthenticatedMixin, FormView, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite crear un usuario

    """

    form_class = forms.UserCreateForm
    template_name = 'administracion/user_create_delete.html'

    section_title = 'Nuevo Usuario'
    left_active = 'Usuarios'


    def get_context_data(self, **kwargs):

        context = super(UserCreateView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions_context(context)

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active

        return context

    def get_success_url(self):
        return reverse(base_settings.ADM_USER_LIST)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):

        context = {
            'form' : form
        }

        return super(UserCreateView, self).render_to_response(self.get_context_data(**context))



class UserListView(UserIsAuthenticatedMixin, ListView, UrlNamesContextMixin, UserPermissionContextMixin):

    """
    Clase correspondiente a la vista que lista los usuarios


    """
    model = User
    context_object_name = 'user_list'
    template_name = 'administracion/user_list.html'

    section_title = 'Lista de Usuarios'
    left_active = 'Usuarios'

    allow_empty = True

    paginate_by = 10

    def get_queryset(self):

        users = []

        for u in User.objects.all():

            # No lista los usuarios que estan desactivados
            if not u.user.is_active:
                continue

            u.can_delete = True
            # Verifica que los proyectos esten en estado pendiente, cancelado o finalizado para poder eliminar
            for p in u.get_projects():
                if p[0].get_state() == 'Ejecucion':
                    u.can_delete = False
                    break

            users.append(u)


        return users

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions_context(context)

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active

        return context

class UserDeleteView(UserCreateView):
    """
    Clase correspondiente a la vista que permite eliminar un rol usuario

    """


    form_class = forms.UserDeleteForm

    section_title = 'Borrar Usuario'

    user_id_kwname = 'user_id'

    def get(self, request, *args, **kwargs):

        if str(request.user.user.id) == kwargs.get(self.user_id_kwname):
            from scrunban.settings.base import ADM_USER_LIST
            return HttpResponseRedirect(reverse(ADM_USER_LIST))

        form = self.form_class(self.get_initial())

        if (form.is_valid()):
            return super(UserDeleteView, self).get(request, *args, **kwargs)
        else:
            from scrunban.settings.base import ADM_USER_LIST

            return HttpResponseRedirect(reverse(ADM_USER_LIST))

    def post(self, request, *args, **kwargs):
        if str(request.user.user.id) == kwargs.get(self.user_id_kwname):
            from scrunban.settings.base import ADM_USER_LIST
            return HttpResponseRedirect(reverse(ADM_USER_LIST))
        else:
            return super(UserDeleteView, self).post(self, request, *args, **kwargs)

    def get_initial(self):
        id = self.kwargs.get(self.user_id_kwname)

        user = get_object_or_404(User, id=id)
        self.user = user

        initial = {
            'id' : user.id,
            'username' : user.get_username(),
            'first_name' : user.get_first_name(),
            'last_name' : user.get_last_name(),
            'direccion' : user.get_direccion(),
            'telefono' : user.get_telefono(),
            'email' : user.get_email()
        }
        return initial

    def get_context_data(self, **kwargs):

        context = super(UserDeleteView, self).get_context_data(**kwargs)

        context['no_editable'] = True
        context['delete_form'] = True
        context['user_projects'] = []

        for p in self.user.get_projects():
            names = [r.desc_larga for r in p[1]]
            p[0].state = p[0].get_state()
            context['user_projects'].append((p[0], ', '.join(names)))

        return context

@login_required()
def user_story_create(request, project):
    context = {
        'section_title':'User Story',
        'URL_NAMES': base_settings.URL_NAMES,
        'project': Project.projects.get(pk=project),
    }
    x = UserPermissionContextMixin()
    x.project = context['project']
    x.request = request
    x.get_user_permissions_context(context)
    if request.method == 'POST':
        form = UserStoryForm(context['project'], request.POST)
        if form.is_valid():
            # TODO Validate project!
            # Create new user story
            data = form.cleaned_data
            data['project'] = Project.projects.get(pk=project)

            us_type = UserStoryType.objects.get(id=data['us_type_'])
            data.pop('us_type_', None)
            us = UserStory.user_stories.create(**data)
            us.us_type = us_type
            us.save()

            # Log event
            kwargs = {
                'entity': 'User Story {}'.format(us.description),
                'project': context['project'].name,
                'action': 'creado',
                'actor': request.user.get_full_name()
            }
            stdlogger.info(formatter(**kwargs))
            
            # Redirect to the new user story summary page!
            return redirect(base_settings.ADM_US_LIST, project=project)
        else:
            context['form'] = form
    else:
        # TODO Check project id
        context['form'] = UserStoryForm(context['project'])

    return render(request, 'administracion/user_story/create', context)

@login_required()
def user_story_summary(request, project, user_story):
    # TODO Check user permissions
    # TODO Check project id
    # TODO Check userstory id

    us = UserStory.user_stories.get(pk=user_story)
    us.state = UserStory.states[us.state]
    context = {
        'section_title':'User Story',
        'URL_NAMES': base_settings.URL_NAMES,
        'project': Project.projects.get(pk=project),
        'user_story': us
    }

    x = UserPermissionContextMixin()
    x.project = context['project']
    x.request = request
    x.get_user_permissions_context(context)
    return render(request, 'administracion/user_story/summary', context)

@login_required()
def user_story_list(request, project):
    project_instance = Project.projects.get(pk=project)
    context = {
        'section_title':'User Story',
        'URL_NAMES': base_settings.URL_NAMES,
        'project': project_instance,
        'user_stories': UserStory.user_stories.filter(project=project_instance)
    }
    x = UserPermissionContextMixin()
    x.project = context['project']
    x.request = request
    x.get_user_permissions_context(context)
    return render(request, 'administracion/user_story/list', context)

@login_required()
def user_story_delete(request, project, user_story):
    # TODO Check permissions
    # TODO Check project and us
    us = UserStory.user_stories.get(pk=user_story)

    # Log event
    kwargs = {
        'entity': 'User Story {}'.format(us.description),
        'project': Project.projects.get(pk=project).name,
        'action': 'eliminado',
        'actor': request.user.get_full_name()
    }
    stdlogger.info(formatter(**kwargs))        
    
    us.delete()
    return redirect(base_settings.ADM_US_LIST, project=project)

@login_required()
def user_story_type_create(request, project):
    # TODO Check project
    context = {
        'section_title':'Tipo de User Story',
        'URL_NAMES': base_settings.URL_NAMES,
        'project': Project.projects.get(pk=project),
    }
    x = UserPermissionContextMixin()
    x.project = context['project']
    x.request = request
    x.get_user_permissions_context(context)
    if request.method == 'POST':
        # TODO Flow (if belongs to project)
        form = UserStoryTypeForm(context['project'], request.POST)
        if form.is_valid():
            ust = UserStoryType.types.create(name=form.cleaned_data['name'], project=context['project'])
            for flow in form.cleaned_data['flows']:
                ust.flows.add(Flow.flows.get(pk=flow))

            # Log event
            kwargs = {
                'entity': 'Tipo de User Story {}'.format(ust.name),
                'project': context['project'].name,
                'action': 'creado',
                'actor': request.user.get_full_name()
            }
            stdlogger.info(formatter(**kwargs))
            
            return redirect(base_settings.ADM_UST_LIST, project=project)
        else:
            context['form'] = form

    else:
        context['form'] = UserStoryTypeForm(context['project'])
    return render(request, 'administracion/user_story_type/create', context)


@login_required()
def user_story_type_list(request, project):
    context = {
        'section_title':'Tipo de User Story',
        'URL_NAMES': base_settings.URL_NAMES,
        'project': Project.projects.get(pk=project),
        'user_story_types': UserStoryType.types.filter(flows__project=project).distinct().order_by('name')
    }

    tus_list = []
    from apps.administracion.models import Grained
    from apps.proyecto.models import Sprint

    for s in Sprint.objects.filter(project=context['project']):
        for g in Grained.objects.filter(sprint=s):
            if not(g.user_story.us_type in tus_list):
                tus_list.append(g.user_story.us_type)

    for tus in context['user_story_types']:
        tus.removable = True
        if tus in tus_list:
            tus.removable = False

    x = UserPermissionContextMixin()
    x.project = context['project']
    x.request = request
    x.get_user_permissions_context(context)
    return render(request, 'administracion/user_story_type/list', context)

@login_required()
def user_story_type_delete(request, project, user_story_type):
    # TODO Check project, permissions and ust
    ust = UserStoryType.types.get(pk=user_story_type)

    # Log event
    kwargs = {
        'entity': 'Tipo de User Story {}'.format(ust.name),
        'project': Project.projects.get(pk=project).name,
        'action': 'eliminado',
        'actor': request.user.get_full_name()
    }
    stdlogger.info(formatter(**kwargs))
    
    ust.delete()
    return redirect(base_settings.ADM_UST_LIST, project=project)


@login_required()
def flow_create(request, project):
    context = {
        'section_title':'Tipo de User Story',
        'URL_NAMES': base_settings.URL_NAMES,
        'project': Project.projects.get(pk=project),
    }
    if request.method == 'POST':
        form = FlowForm(request.POST)
        if form.is_valid():
            # TODO Check project
            Flow.flows.create(
                name=form.cleaned_data['name'],
                project=Project.projects.get(pk=project)
            )

            # Log event
            kwargs = {
                'entity': 'Flujo',
                'project': context['project'].name,
                'action': 'eliminado',
                'actor': request.user.get_full_name()
            }
            stdlogger.info(formatter(**kwargs))
            
        return redirect(base_settings.ADM_FLW_LIST, project=project)
    else:
        # TODO Check project
        context = {
            'section_title':'Flujo',
            'URL_NAMES': base_settings.URL_NAMES,
            'project': Project.projects.get(pk=project),
            'form': FlowForm()
        }
        return render(request, 'administracion/flow/create', context)

@login_required()
def flow_list(request, project):
    # TODO Check project
    context = {
        'section_title':'Flujo',
        'URL_NAMES': base_settings.URL_NAMES,
        'project': Project.projects.get(pk=project),
        'flows': Flow.flows.filter(project=project)
    }
    return render(request, 'administracion/flow/list', context)

@login_required()
def flow_delete(request, project, flow):
    # TODO Check everything!!
    flow = Flow.flows.get(pk=flow)

    # Log event
    kwargs = {
        'entity': 'Flujo',
        'project': Project.projects.get(pk=project).name,
        'action': 'eliminado',
        'actor': request.user.get_full_name()
    }
    stdlogger.info(formatter(**kwargs))
    
    flow.delete()
    return redirect(base_settings.ADM_FLW_LIST, project=project)

@login_required()
def flow_summary(request, project, flow):
    if request.method == 'POST':
        flow = Flow.flows.get(pk=flow)
        form = FlowForm(request.POST, instance=flow)
        if form.is_valid():
            form.save()
        return redirect(base_settings.ADM_FLW_LIST, project=project)
    else:
        context = {
            'section_title':'Flujo',
            'URL_NAMES': base_settings.URL_NAMES,
            'project': Project.projects.get(pk=project),
            'form': FlowForm(instance=Flow.flows.get(pk=flow))
        }
        return render(request, 'administracion/flow/summary', context)

@login_required()
def notification_list(request):
    return render(request, 'administracion/notification/list')
    
