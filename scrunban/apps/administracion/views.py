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


# Create your views here.
def index(request):
    """
    menu
    """
    return HttpResponse("<html><body><h1>Main Menu</h1><a href='http://localhost:8000/adm/proyecto/nuevo'>Nuevo Proyecto</a><br>"
                        "<a href='http://localhost:8000/adm/proyecto/eliminar'>Eliminar Proyecto</a></body></html>")


@login_required("proyecto_crear")
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


@login_required("adm:proyecto_eliminar")
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
    }
    if request.method == 'POST':
        try:
            p = Project.objects.get(name=request.POST['project'])
            p.delete()
        except KeyError:
            x = None
        return render(request, 'proyectoEliminar.html', context)
    return render(request, 'proyectoEliminar.html', context)


