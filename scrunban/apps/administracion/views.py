from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import ProjectForm
from .models import Project
from .models import ProductBacklog
from apps.autenticacion.models import User
from scrunban.settings import base as base_settings
from apps.autenticacion.decorators import login_required
from django.db.utils import IntegrityError

#Todo! look at this
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from apps.administracion.models import Project

from apps.administracion import forms
from django.shortcuts import get_object_or_404, HttpResponseRedirect

from apps.proyecto.mixins import UrlNamesContextMixin
from apps.autenticacion.mixins import UserPermissionContextMixin

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from scrunban.settings import base as base_settings


# Create your views here.
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
            print("Received!")
            p = Project()
            p.name = form.cleaned_data['name']
            p.date_start = form.cleaned_data['date_start']
            p.date_end = form.cleaned_data['date_end']
            sm = User.users.filter(username=form.cleaned_data['scrum_master']).get()
            p.scrum_master = sm
            po = User.users.filter(username=form.cleaned_data['product_owner']).get()
            p.product_owner = po
            pb = ProductBacklog()
            pb.save()
            p.product_backlog = pb

            try:
                p.save()

                # Crea roles por defecto
                from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES
                from django.contrib.auth.models import Permission

                for rol in DEFAULT_PROJECT_ROLES:
                    role_data = {
                        'name': rol[0],
                        'desc_larga':  rol[1]
                    }

                    new_rol = p.add_rol(**role_data)
                    for perm_ in rol[2]:
                        perm = Permission.objects.get(codename=perm_[0])
                        new_rol.add_perm(perm)


                p_id = p.id
                for rol in p.get_roles():
                    if rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[0][0]:
                        rol.add_user(User.users.get(username=form.cleaned_data['scrum_master']))
                    elif rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[1][0]:
                        rol.add_user(User.users.get(username=form.cleaned_data['product_owner']))




            except IntegrityError as e:
                print(e)
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


class UserCreateView(FormView, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite crear un usuario

    """

    form_class = forms.UserCreateForm
    template_name = 'administracion/user_create_delete.html'

    section_title = 'Nuevo Usuario'
    left_active = 'Usuarios'

    @method_decorator(login_required(login_url=base_settings.LOGIN_NAME))
    def dispatch(self, *args, **kwargs):
        return super(UserCreateView, self).dispatch(*args, **kwargs)

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
        print('valid form')
        print(form)
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):

        print(form)

        context = {
            'form' : form
        }

        return super(UserCreateView, self).render_to_response(self.get_context_data(**context))



class UserListView(ListView, UrlNamesContextMixin, UserPermissionContextMixin):

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

    @method_decorator(login_required(login_url=base_settings.LOGIN_NAME))
    def dispatch(self, *args, **kwargs):
        return super(UserListView, self).dispatch(*args, **kwargs)

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
