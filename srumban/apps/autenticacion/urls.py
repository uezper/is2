"""srumban URL Configuration

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
from apps.autenticacion import views

#LOGIN_NAME  = 'auth_name' # TODO Centralize this type of data!
#AUTH_NAME   = 'auth_auth'
#DEAUTH_NAME = 'auth_deauth'
# Con el "app_name = 'auth'", ahora se escribe
#   auth:name
#   auth:auth
#   auth:deauth
#   auth:app
#   auth:app2
#   auth:data

app_name = 'auth'
urlpatterns = [
    url(r'^$', views.login, name='name'),
    url(r'^authenticate_user/$', views.authenticate_user, name='auth'),
    url(r'^deauthenticate_user/$', views.deauthenticate_user, name='deauth'),
    
    url(r'^app/$', views.app, name='app'), # TODO Remove when app url ready!
    url(r'^app2/$', views.app2, name='app2'),
    url(r'^data/$', views.data, name='data'),
]
