from django.conf.urls import url

from . import views

app_name = 'adm'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^proyecto/nuevo$', views.crear_proyecto, name='proyecto_nuevo'),
    url(r'^proyecto/eliminar', views.eliminar_proyecto, name='proyecto_eliminar'),
]

