from django.conf.urls import url
from scrunban.settings import base as base_settings
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^(?P<project_id>[0-9]+)/$', views.index,
        name=base_settings.PROJECT_INDEX),
    url(r'^(?P<project_id>[0-9]+)/roles/$', views.RoleListView.as_view(),
        name=base_settings.PROJECT_ROLE_LIST),
    url(r'^(?P<project_id>[0-9]+)/roles/create/$', views.RoleCreateView.as_view(),
        name=base_settings.PROJECT_ROLE_CREATE),
    url(r'^(?P<project_id>[0-9]+)/roles/edit/(?P<rol_id>[0-9]+)/$', views.RoleEditView.as_view(),
        name=base_settings.PROJECT_ROLE_EDIT),
    url(r'^(?P<project_id>[0-9]+)/roles/delete/(?P<rol_id>[0-9]+)/$', views.RoleDeleteView.as_view(),
        name=base_settings.PROJECT_ROLE_DELETE),
]

