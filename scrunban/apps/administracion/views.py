from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import ProjectForm
from .models import Proyecto
from .models import ProductBacklog
from apps.autenticacion.models import User
from scrunban.settings import base as base_settings
from apps.autenticacion.decorators import login_required

# Create your views here.
def index (request):
    return HttpResponse("<html><body><h1>Main Menu</h1><a href='http://localhost:8000/adm/proyecto/nuevo'>Nuevo Proyecto</a></body></html>")

@login_required("adm:proyectoCrear")
def crear_proyecto(request):
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
            p = Proyecto()
            p.nombre = form.cleaned_data['nombre']
            p.fechaInicio = form.cleaned_data['fechaInicio']
            p.fechaFinal = form.cleaned_data['fechaFinal']
            sm = User.users.filter(username=form.cleaned_data['scrumMaster']).get()
            p.scrumMaster = sm
            po = User.users.filter(username=form.cleaned_data['productOwner']).get()
            p.productOwner = po
            pb = ProductBacklog()
            pb.save()
            p.productBacklog = pb
            p.save()
            #return HttpResponseRedirect(reverse('adm:proyectoNuevo'))
            return render(request, 'proyectoCrearExitoso.html', context)
    else:
        form = ProjectForm()
        context['form'] = form
    return render(request, 'proyectoCrear.html', context)

@login_required("adm:proyectoEliminar")
def eliminar_proyecto(request):
    context = {
        "PERFIL_NAME": base_settings.PERFIL_NAME,
        "DEAUTH_NAME": base_settings.DEAUTH_NAME,
        "LOGIN_NAME": base_settings.LOGIN_NAME,
        "proyecto_list": Proyecto.objects.all(),
    }
    if request.method == 'POST':
        try:
            p = Proyecto.objects.get(nombre=request.POST['proyecto'])
            p.delete()
        except KeyError:
            x = None
        return render(request, 'proyectoEliminar.html', context)
    return render(request, 'proyectoEliminar.html', context)


