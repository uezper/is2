from django.conf.urls import url
from scrunban.settings import base as base_settings
from . import views

urlpatterns = [
    url(r'^proyecto/nuevo', views.crear_proyecto, name=base_settings.ADM_PROJECT_CREATE),
    url(r'^proyecto/eliminar', views.eliminar_proyecto, name=base_settings.ADM_PROJECT_DELETE),
    url(r'^users/$', views.UserListView.as_view(), name=base_settings.ADM_USER_LIST),
    url(r'^users/create', views.UserCreateView.as_view(), name=base_settings.ADM_USER_CREATE),
    url(r'^users/delete/(?P<user_id>[0-9]+)', views.UserDeleteView.as_view(), name=base_settings.ADM_USER_DELETE),
    url(r'^userstory/create', views.user_story_create, name=base_settings.ADM_US_CREATE),
    url(r'^userstory/summary', views.user_story_summary, name='us_summary'),
    #url(r'^$', views.UserListView.as_view()),
]

