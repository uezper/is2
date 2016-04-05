import json, pdb
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
#from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate as djAuthenticate
from django.contrib.auth import login as djLogin
from django.contrib.auth import logout as djLogout
from autenticacion.decorators import login_required

def login(request):
    request.session.set_test_cookie() # For cookie-based sessions
    return render(request, 'login')

def authenticate_user(request):
    data = {} # Container for the ajax response
        
    if request.method == 'POST' and request.is_ajax():

        if request.is_ajax():
            
            if not request.session.test_cookie_worked():
                data['message'] = 'Necesito utilizar cookies!.'
                data['STATUS'] = 'ERROR'
                return HttpResponse(json.dumps(data), content_type='application/json')

            fromClient = json.loads(request.body.decode('utf-8'))
        
            if 'username' not in fromClient or 'password' not in fromClient:
                #TODO Fix this with a proper error! (Probably a manually build request)
                data['message'] = 'Sucedió algo inesperado!.'
                data['STATUS'] = 'ERROR'
                return HttpResponse(json.dumps(data), content_type='application/json')

            user = djAuthenticate(username = fromClient['username'], password = fromClient['password'])
            if user is not None:
                if user.is_active:
                    #TODO And if there is a request of login of a already loged in user?
                    djLogin(request, user)
                    data['message'] = 'Bienvenido! Redireccionandote...'
                    data['STATUS'] = 'OK'
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    data['message'] = 'Cuenta desactivada.'
                    data['STATUS'] = 'ERROR'
                    return HttpResponse(json.dumps(data), content_type='application/json')
            
            else:
                data['message'] = 'Usuario y contraseña inválidos.'
                data['STATUS'] = 'ERROR'
                return HttpResponse(json.dumps(data), content_type='application/json')
        
    else:
        #TODO Fix this with a proper error! (Probably a manually build request)
        data['message'] = 'Sucedió algo inesperado!.'
        return HttpResponse(json.dumps(data), content_type='application/json')

def deauthenticate_user(request):
    djLogout(request)
    #TODO On logout, redirect to login?
    return HttpResponseRedirect('/auth/')

"""
Dummy view, waiting for the app implementation!
"""
@login_required('auth_app')
def app(request):
    user = request.user
    return HttpResponse('Hi, {}! <a href={}>Logout</a>'.format(user.first_name, '/auth/deauthenticate_user/'))

"""
"""
@login_required('auth_app2')
def app2(request):
    return HttpResponse('Hi!, you\'re in a private area.')

def data(request):
    user = request.user
    return HttpResponse('You are {}'.format(user))
