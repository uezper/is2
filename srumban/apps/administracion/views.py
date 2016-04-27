from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import ProjectForm
from .models import Usuario
from .models import Proyecto
from .models import ProductBacklog
# Create your views here.
def index (request):
    return HttpResponse("<html><body><h1>Main Menu</h1><a href='http://localhost:8000/adm/proyecto/nuevo'>Nuevo Proyecto</a></body></html>")

def crearProyecto(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            print("Received!")
            p = Proyecto()
            p.nombre = form.cleaned_data['nombre']
            p.fechaInicio = form.cleaned_data['fechaInicio']
            p.fechaFinal = form.cleaned_data['fechaFinal']
            sm = Usuario.objects.get(nombre=form.cleaned_data['scrumMaster'])
            p.scrumMaster = sm
            po = Usuario.objects.get(nombre=form.cleaned_data['productOwner'])
            p.productOwner = po
            pb = ProductBacklog()
            pb.save()
            p.productBacklog = pb
            p.save()
            #return HttpResponseRedirect(reverse('adm:proyectoNuevo'))
            return HttpResponse("Gotcha! :D")
    else:
        form = ProjectForm()
    userList = Usuario.objects.all()
    return render(request, 'crearProyecto.html', {'form': form, 'userList':userList})
