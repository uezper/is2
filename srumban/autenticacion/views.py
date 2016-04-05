import json
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate as djAuthenticate
from django.contrib.auth import login as djLogin
from django.contrib.auth import logout as djLogout
from autenticacion.decorators import login_required
from autenticacion import urls

def login(request):
    #TODO If user already "loged in", redirect... somewhere...
    request.session.set_test_cookie() # For cookie-based sessions
    return render(request, 'login')

def authenticate_user(request):
    data = {} # Container for the ajax response
        
    if request.method == 'POST' and request.is_ajax():

        if request.is_ajax():
            
            if not request.session.test_cookie_worked():
                data['message'] = 'Necesito utilizar cookies!.'
                data['STATUS'] = 'ERROR'
                return JsonResponse(data)

            # TODO User a proper form!
            fromClient = json.loads(request.body.decode('utf-8'))
        
            if 'username' not in fromClient or 'password' not in fromClient:
                #TODO Fix this with a proper error! (Probably a manually build request)
                data['message'] = 'Sucedió algo inesperado!.'
                data['STATUS'] = 'ERROR'
                return JsonResponse(data)

            user = djAuthenticate(username = fromClient['username'], password = fromClient['password'])
            if user is not None:
                if user.is_active:
                    #TODO And if there is a request of login of a already loged in user?
                    djLogin(request, user)
                    data['message'] = 'Bienvenido! Redireccionandote...'
                    data['STATUS'] = 'OK'
                    return JsonResponse(data)

                else:
                    data['message'] = 'Cuenta desactivada.'
                    data['STATUS'] = 'ERROR'
                    return JsonResponse(data)
            
            else:
                data['message'] = 'Usuario y contraseña inválidos.'
                data['STATUS'] = 'ERROR'
                return JsonResponse(data)
        
    else:
        #TODO Fix this with a proper error! (Probably a manually build request)
        data['message'] = 'Sucedió algo inesperado!.'
        data['STATUS']  = 'ERROR'
        return JsonResponse(data)

def deauthenticate_user(request):
    djLogout(request)
    #TODO On logout, redirect to login?
    return HttpResponseRedirect(reverse(urls.LOGIN_NAME))

"""
Dummy view
"""
@login_required('auth_app')
def app(request):
    user = request.user
    return HttpResponse('Hi, {}! <a href={}>Logout</a>'.format(user.first_name, '/auth/deauthenticate_user/'))

"""
Dummy view
"""
@login_required('auth_app2')
def app2(request):
    return HttpResponse('Hi!, you\'re in a private area.')

"""
Dummy view
"""
def data(request):
    user = request.user
    return HttpResponse('You are {}'.format(user))
