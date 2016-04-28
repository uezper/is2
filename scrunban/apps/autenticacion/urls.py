"""scrunban URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from scrunban.settings import base as base_settings
from apps.autenticacion import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', views.login, name=base_settings.LOGIN_NAME),
    url(r'^authenticate_user/$', views.authenticate_user, name=base_settings.AUTH_NAME),
    url(r'^deauthenticate_user/$', views.deauthenticate_user, name=base_settings.DEAUTH_NAME),
    

    url(r'^perfil/$', views.perfil, name=base_settings.PERFIL_NAME),

    # TODO! Cambiar cuando este la nueva app
    url(r'^project/(?P<project_id>[0-9]+)/roles/$', views.role_list, name=base_settings.PROJECT_ROLE_LIST),
    url(r'^project/(?P<project_id>[0-9]+)/roles/create/$', views.role_create, name=base_settings.PROJECT_ROLE_CREATE),
    url(r'^project/(?P<project_id>[0-9]+)/roles/delete/(?P<rol_id>[0-9]+)/$', views.rol_delete, name=base_settings.PROJECT_ROLE_DELETE),
    url(r'^project/(?P<project_id>[0-9]+)/roles/(?P<rol_id>[0-9]+)/$', views.rol_detail, name=base_settings.PROJECT_ROLE_DETAIL),
    url(r'^project/(?P<project_id>[0-9]+)/roles/edit/(?P<rol_id>[0-9]+)/$', views.role_edit, name=base_settings.PROJECT_ROLE_EDIT),
]
