from django.conf.urls import url
from scrunban.settings import base as base_settings
from . import views

urlpatterns = [
    url(r'^(?P<project_id>[0-9]+)/$', views.index,
        name=base_settings.PROJECT_INDEX),
    url(r'^(?P<project_id>[0-9]+)/role/$', views.RoleListView.as_view(),
        name=base_settings.PROJECT_ROLE_LIST),
    url(r'^(?P<project_id>[0-9]+)/role/create/$', views.RoleCreateView.as_view(),
        name=base_settings.PROJECT_ROLE_CREATE),
    url(r'^(?P<project_id>[0-9]+)/role/edit/(?P<rol_id>[0-9]+)/$', views.RoleEditView.as_view(),
        name=base_settings.PROJECT_ROLE_EDIT),
    url(r'^(?P<project_id>[0-9]+)/role/delete/(?P<rol_id>[0-9]+)/$', views.RoleDeleteView.as_view(),
        name=base_settings.PROJECT_ROLE_DELETE),
    url(r'^(?P<project_id>[0-9]+)/dev/$', views.DevListView.as_view(),
        name=base_settings.PROJECT_DEV_LIST),
    url(r'^(?P<project_id>[0-9]+)/dev/edit/(?P<team_id>[0-9]+)/$', views.DevEditView.as_view(),
        name=base_settings.PROJECT_DEV_EDIT),
    url(r'^(?P<project_id>[0-9]+)/sprint/$', views.SprintListView.as_view(),
        name=base_settings.PROJECT_SPRINT_LIST),
    url(r'^(?P<project_id>[0-9]+)/sprint/create/$', views.SprintCreateView.as_view(),
        name=base_settings.PROJECT_SPRINT_CREATE),
    url(r'^(?P<project_id>[0-9]+)/sprint/edit/(?P<sprint_id>[0-9]+)/$', views.SprintEditView.as_view(),
        name=base_settings.PROJECT_SPRINT_EDIT),
    url(r'^(?P<project_id>[0-9]+)/sprint/delete/(?P<sprint_id>[0-9]+)/$', views.SprintDeleteView.as_view(),
        name=base_settings.PROJECT_SPRINT_DELETE),
    url(r'^(?P<project_id>[0-9]+)/sprint/detail/(?P<sprint_id>[0-9]+)/$', views.SprintDetailView.as_view(),
        name=base_settings.PROJECT_SPRINT_DETAIL),
    url(r'^(?P<project_id>[0-9]+)/flow/create/$', views.FlowCreateView.as_view(),
        name=base_settings.PROJECT_FLOW_CREATE),
    url(r'^(?P<project_id>[0-9]+)/flow/$', views.FlowListView.as_view(),
        name=base_settings.PROJECT_FLOW_LIST),
    url(r'^(?P<project_id>[0-9]+)/flow/edit/(?P<flow_id>[0-9]+)/$', views.FlowEditView.as_view(),
        name=base_settings.PROJECT_FLOW_EDIT),
    url(r'^(?P<project_id>[0-9]+)/flow/delete/(?P<flow_id>[0-9]+)/$', views.FlowDeleteView.as_view(),
        name=base_settings.PROJECT_FLOW_DELETE),
]

