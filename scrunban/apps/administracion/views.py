from django.shortcuts import render
from django.http import HttpResponse
from .forms import ProjectForm, UserStoryCreateForm
from apps.autenticacion.models import User
from apps.autenticacion.decorators import login_required
from django.db.utils import IntegrityError

#Todo! look at this
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from apps.proyecto.models import Project
from apps.administracion.models import UserStory
from apps.administracion import forms
from django.shortcuts import get_object_or_404, HttpResponseRedirect

from apps.proyecto.mixins import UrlNamesContextMixin
from apps.autenticacion.mixins import UserPermissionContextMixin, UserIsAuthenticatedMixin

from scrunban.settings import base as base_settings

def index(request):
    """
    menu
    """
    return HttpResponse("<html><body><h1>Main Menu</h1><a href='http://localhost:8000/adm/proyecto/nuevo'>Nuevo Proyecto</a><br>"
                        "<a href='http://localhost:8000/adm/proyecto/eliminar'>Eliminar Proyecto</a></body></html>")


@login_required()
def crear_proyecto(request):
    """
    Retorna la vista correspondiente a la página de creacion de proyecto.

    :param request: Los datos de la solicitud

    :returns: Un 'renderizado' del template correspondiente.
    """
    context = {
        'user_list': User.objects.all(),
        'URL_NAMES' : base_settings.URL_NAMES,
        'left_active': 'Nuevo Proyecto'
    }
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        context['form'] = form
        if form.is_valid():

            data = {
                'name': form.cleaned_data['name'],
                'date_start': form.cleaned_data['date_start'],
                'date_end': form.cleaned_data['date_end'],
                'scrum_master': User.users.filter(username=form.cleaned_data['scrum_master']).get(),
                'product_owner': User.users.filter(username=form.cleaned_data['product_owner']).get()
            }

            p = Project.projects.create(**data)
            if p == None:
                form.add_error('name', 'Project name already exist')
                return render(request, 'administracion/proyectoCrear.html', context)
            return render(request, 'administracion/proyectoCrearExitoso.html', context)
    else:
        form = ProjectForm()
        context['form'] = form
    return render(request, 'administracion/proyectoCrear.html', context)


@login_required()
def eliminar_proyecto(request):
    """

    Retorna la vista correspondiente a la pagina de creacion de proyecto.

    :param request: Los datos de la solicitud

    :returns: Un 'renderizado' del template correspondiente.

    """
    context = {
        "project_list": Project.objects.all(),
        'URL_NAMES': base_settings.URL_NAMES,
        'left_active': 'Eliminar Proyecto'
    }
    if request.method == 'POST':
        try:
            p = Project.objects.get(name=request.POST['project'])
            p.delete()
        except KeyError:
            x = None
        return render(request, 'administracion/proyectoEliminar.html', context)
    return render(request, 'administracion/proyectoEliminar.html', context)


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
        self.get_user_permissions(context)

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
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions(context)

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
            context['user_projects'].append((p[0], ', '.join(names)))

        return context

@login_required()
def user_story_create(request, project):
    if request.method == 'POST':
        form = UserStoryCreateForm(request.POST)
        if form.is_valid():
            # TODO Validate project!
            # Create new user story
            data = form.cleaned_data
            data['project'] = Project.projects.get(pk=project)
            us = UserStory.user_stories.create(**data)
            # Redirect to the new user story summary page!
            context = {
                'URL_NAMES': base_settings.URL_NAMES,
                'project': us.project,
                'user_story': us
            }
            #return HttpResponseRedirect('administracion/user_story/summary')
            return render(request, 'administracion/user_story/summary', context)
    else:
        # TODO Check project id
        context = {
            'URL_NAMES': base_settings.URL_NAMES,
            'project': Project.projects.get(pk=project),
            'form': UserStoryCreateForm()
        }
        return render(request, 'administracion/user_story/create', context)

@login_required()
def user_story_summary(request, project, user_story):
    # TODO Check user permissions
    # TODO Check project id
    # TODO Check userstory id
    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project': Project.projects.get(pk=project),
        'user_story': UserStory.user_stories.get(pk=user_story)
    }
    return render(request, 'administracion/user_story/summary', context)

@login_required()
def user_story_list(request, project):
    project_instance = Project.projects.get(pk=project)
    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project': project_instance,
        'user_stories': UserStory.user_stories.filter(project=project_instance)
    }
    return render(request, 'administracion/user_story/list', context)
