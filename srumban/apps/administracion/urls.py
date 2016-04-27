from django.conf.urls import url

from . import views

app_name = 'adm'
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^proyecto/nuevo$', views.crearProyecto, name = 'proyectoNuevo'),
]

