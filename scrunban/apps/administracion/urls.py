from django.conf.urls import url
from scrunban.settings import base as base_settings
from . import views

urlpatterns = [
    url(r'^proyecto/nuevo', views.crear_proyecto, name=base_settings.ADM_PROJECT_CREATE),
    url(r'^proyecto/eliminar', views.eliminar_proyecto, name=base_settings.ADM_PROJECT_DELETE),
    url(r'^proyecto/(?P<project>\d+)/userstory/$', views.user_story_list, name=base_settings.ADM_US_LIST),
    url(r'^proyecto/(?P<project>\d+)/userstory/create', views.user_story_create, name=base_settings.ADM_US_CREATE),
    url(r'^proyecto/(?P<project>\d+)/userstory/(?P<user_story>\d+)/delete', views.user_story_delete, name=base_settings.ADM_US_DELETE),
    url(r'^proyecto/(?P<project>\d+)/userstory/(?P<user_story>\d+)', views.user_story_summary, name=base_settings.ADM_US_SUMMARY),
    
    url(r'^users/$', views.UserListView.as_view(), name=base_settings.ADM_USER_LIST),
    url(r'^users/create', views.UserCreateView.as_view(), name=base_settings.ADM_USER_CREATE),
    url(r'^users/delete/(?P<user_id>[0-9]+)', views.UserDeleteView.as_view(), name=base_settings.ADM_USER_DELETE),

    #url(r'^$', views.UserListView.as_view()),
]

