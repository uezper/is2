from django.conf.urls import url
from scrunban.settings import base as base_settings
from . import views

urlpatterns = [
    url(r'^project/$', views.ProjectListView.as_view(), name=base_settings.ADM_PROJECT_LIST),
    url(r'^project/new/$', views.ProjectCreateViewTest.as_view(), name=base_settings.ADM_PROJECT_CREATE),
    url(r'^project/edit/(?P<pk>[0-9]+)/$', views.ProjectModifyView.as_view(), name=base_settings.ADM_PROJECT_MODIFY),
    url(r'^project/delete/(?P<pk>[0-9]+)/$', views.ProjectDeleteView.as_view(), name=base_settings.ADM_PROJECT_DELETE),

    url(r'^proyecto/(?P<project>\d+)/userstory/$', views.user_story_list, name=base_settings.ADM_US_LIST),
    url(r'^proyecto/(?P<project>\d+)/userstory/create$', views.user_story_create, name=base_settings.ADM_US_CREATE),
    url(r'^proyecto/(?P<project>\d+)/userstory/(?P<user_story>\d+)/delete$', views.user_story_delete, name=base_settings.ADM_US_DELETE),
    url(r'^proyecto/(?P<project>\d+)/userstory/(?P<user_story>\d+)$', views.user_story_summary, name=base_settings.ADM_US_SUMMARY),
    
    url(r'^proyecto/(?P<project>\d+)/userstorytype/$', views.user_story_type_list, name=base_settings.ADM_UST_LIST),
    url(r'^proyecto/(?P<project>\d+)/userstorytype/create$', views.user_story_type_create, name=base_settings.ADM_UST_CREATE),
    url(r'^proyecto/(?P<project>\d+)/userstorytype/(?P<user_story_type>\d+)/delete$', views.user_story_type_delete, name=base_settings.ADM_UST_DELETE),

    url(r'^proyecto/(?P<project>\d+)/flow/$', views.flow_list, name=base_settings.ADM_FLW_LIST),
    url(r'^proyecto/(?P<project>\d+)/flow/create$', views.flow_create, name=base_settings.ADM_FLW_CREATE),
    url(r'^proyecto/(?P<project>\d+)/flow/(?P<flow>\d+)/delete$', views.flow_delete, name=base_settings.ADM_FLW_DELETE),
    url(r'^proyecto/(?P<project>\d+)/flow/(?P<flow>\d+)/$', views.flow_summary, name=base_settings.ADM_FLW_SUMMARY),
    
    url(r'^users/$', views.UserListView.as_view(), name=base_settings.ADM_USER_LIST),
    url(r'^users/create', views.UserCreateView.as_view(), name=base_settings.ADM_USER_CREATE),
    url(r'^users/delete/(?P<user_id>[0-9]+)', views.UserDeleteView.as_view(), name=base_settings.ADM_USER_DELETE),

    #url(r'^$', views.UserListView.as_view()),
]

