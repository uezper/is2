import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate as djAuthenticate
from django.contrib.auth import login as djLogin
from django.contrib.auth import logout as djLogout


def login(request):
    print(request.user)
    print(request.session)
    
    request.session.set_test_cookie() # For cookie-based sessions
    return render(request, 'login')

def authenticate_user(request):
    print(request.user)
    print(request.session)
    
    data = {} # Container for the ajax response
        
    if request.method == 'POST' and request.is_ajax():
        
        if not request.session.test_cookie_worked():
            data['message'] = 'Necesito utilizar cookies!.'
            return HttpResponse(json.dumps(data), content_type='application/json')

        fromClient = json.loads(request.body.decode('utf-8'))
        
        if 'username' not in fromClient or 'password' not in fromClient:
            #TODO Fix this with a proper error! (Probably a manually build request)
            data['message'] = 'Sucedió algo inesperado!.'
            return HttpResponse(json.dumps(data), content_type='application/json')

        user = djAuthenticate(username = fromClient['username'], password = fromClient['password'])
        if user is not None:
            if user.is_active:
                #TODO And if there is a request of login of a already loged in user?
                djLogin(request, user)
                data['destination'] = 'app/'
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                data['message'] = 'Cuenta desactivada.'
                return HttpResponse(json.dumps(data), content_type='application/json')
                
        else:
            data['message'] = 'Usuario y contraseña inválidos.'
            return HttpResponse(json.dumps(data), content_type='application/json')
        
    else:
        #TODO Fix this with a proper error! (Probably a manually build request)
        data['message'] = 'Sucedió algo inesperado!.'
        return HttpResponse(json.dumps(data), content_type='application/json')

def deauthenticate_user(request):
    djLogout(request)
    #TODO On logout, redirect to login?
    return HttpResponseRedirect('/auth/login/')

"""
Dummy view, waiting for the app implementation!
"""
@login_required(login_url='/auth/login/') #TODO Improve!
def app(request):
    user = request.user
    print(user)
    print(request.session)
    if user.is_authenticated():
        return HttpResponse('Hi! {} (to logout go to: /login/logout, of course this is temporal...)'.format(user.get_username()))
    else:
        return HttpResponse('Hey, your are not supouse to be here!')
