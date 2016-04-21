from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse

# Create your views here.
def index (request):
    return HttpResponse("<html>Hello World :D</html>")

def crearProyecto(request):

    return render(request, 'crearProyecto.html', {})
