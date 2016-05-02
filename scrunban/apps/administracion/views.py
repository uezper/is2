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
from apps.autenticacion.models import Role
from apps.administracion.models import Project

from apps.administracion import forms
from django.shortcuts import get_object_or_404, HttpResponseRedirect

from apps.proyecto.mixins import UrlNamesContextMixin
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
        "PERFIL_NAME": base_settings.PERFIL_NAME,
        "DEAUTH_NAME": base_settings.DEAUTH_NAME,
        "LOGIN_NAME": base_settings.LOGIN_NAME,
        'user_list': User.objects.all(),
        'URL_NAMES' : base_settings.URL_NAMES
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
            except IntegrityError as e:
                print(e)
                form.add_error('name', 'Project name already exist')
                return render(request, 'proyectoCrear.html', context)
            return render(request, 'proyectoCrearExitoso.html', context)
    else:
        form = ProjectForm()
        context['form'] = form
    return render(request, 'proyectoCrear.html', context)


@login_required()
def eliminar_proyecto(request):
    """

    Retorna la vista correspondiente a la pagina de creacion de proyecto.

    :param request: Los datos de la solicitud

    :returns: Un 'renderizado' del template correspondiente.

    """
    context = {
        "PERFIL_NAME": base_settings.PERFIL_NAME,
        "DEAUTH_NAME": base_settings.DEAUTH_NAME,
        "LOGIN_NAME": base_settings.LOGIN_NAME,
        "project_list": Project.objects.all(),
        'URL_NAMES': base_settings.URL_NAMES
    }
    if request.method == 'POST':
        try:
            p = Project.objects.get(name=request.POST['project'])
            p.delete()
        except KeyError:
            x = None
        return render(request, 'proyectoEliminar.html', context)
    return render(request, 'proyectoEliminar.html', context)


class UserCreateView(FormView, UrlNamesContextMixin):
    """
    Clase correspondiente a la vista que permite crear un usuario

    """

    form_class = forms.UserCreateForm
    template_name = 'administracion/user_create_delete.html'

    section_title = 'Nuevo Usuario'

    @method_decorator(login_required(login_url=base_settings.LOGIN_NAME))
    def dispatch(self, *args, **kwargs):
        return super(UserCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(UserCreateView, self).get_context_data(**kwargs)

        self.get_url_context(context)

        context['section_title'] = self.section_title

        return context

    def get_success_url(self):
        return reverse(base_settings.ADM_USER_LIST)

    def form_valid(self, form):

        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):

        print(form)

        context = {
            'form' : form
        }

        return super(UserCreateView, self).render_to_response(self.get_context_data(**context))



class UserListView(ListView, UrlNamesContextMixin):

    """
    Clase correspondiente a la vista que lista los usuarios


    """
    model = User
    context_object_name = 'user_list'
    template_name = 'administracion/user_list.html'

    section_title = 'Lista de Usuarios'
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

        context['section_title'] = self.section_title

        return context

class UserDeleteView(UserCreateView):
    """
    Clase correspondiente a la vista que permite eliminar un rol usuario

    """


    form_class = forms.UserDeleteForm

    section_title = 'Borrar Usuario'

    user_id_kwname = 'user_id'

    def get(self, request, *args, **kwargs):

        form = self.form_class(self.get_initial())
        print('en get')
        print(form)

        if (form.is_valid()):
            return super(UserDeleteView, self).get(request, *args, **kwargs)
        else:
            from scrunban.settings.base import ADM_USER_LIST

            return HttpResponseRedirect(reverse(ADM_USER_LIST))

    def get_initial(self):
        id = self.kwargs.get(self.user_id_kwname)

        user = get_object_or_404(User, id=id)

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

        return context