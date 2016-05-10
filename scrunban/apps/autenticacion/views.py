import json
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate as djAuthenticate
from django.contrib.auth import login as djLogin
from django.contrib.auth import logout as djLogout
from scrunban.settings import base as base_settings
from apps.autenticacion.decorators import login_required

from apps.autenticacion.mixins import UserPermissionContextMixin


def login(request):
    """
    Retorna la vista correspondiente a la página de login.

    :param request: Los datos de la solicitud

    :returns: Un 'renderizado' del template correspondiente.
    """
    
    if request.user.is_active:
        return HttpResponseRedirect(reverse(base_settings.PERFIL_NAME, args=[request.user.user.id]))

    # For cookie-based sessions
    request.session.set_test_cookie()
    return render(request, 'autenticacion/login')

def authenticate_user(request):
    """
    Autentifica al par usuario:contraseña, vinculando la sesión con el usuario.
    Utiliza AJAX para recibir y responder las solicitudes.

    :param request: Solicitud AJAX con los datos del login.

    :returns:
        - Un JsonRequest con los campos 'message' y 'STATUS' cargados correspondientemente.
        - En caso de ``'STATUS' = 'OK'``, se logeo correctamente al usuario.
        - En caso de ``'STATUS' = 'ERROR'``, occurio un error que se describe en ``'message'``
    """
    #TODO Unify with the login view. Discriminate through request.method and request.is_ajax.

    # Container for the ajax response
    data = {}

    if request.method == 'POST' and request.is_ajax():

        if request.is_ajax():

            if not request.session.test_cookie_worked():
                data['message'] = 'Necesito utilizar cookies!.'
                data['STATUS'] = 'ERROR'
                return JsonResponse(data)

            # TODO User a proper form! (When finish, remove import json)
            from_client = json.loads(request.body.decode('utf-8'))

            if 'username' not in from_client or 'password' not in from_client:
                #TODO Fix this with a proper error! (Probably a manually build request)
                data['message'] = 'Sucedió algo inesperado!.'
                data['STATUS'] = 'ERROR'
                return JsonResponse(data)

            user = djAuthenticate(username=from_client['username'],
                                  password=from_client['password'])
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
        data['STATUS'] = 'ERROR'
        return JsonResponse(data)

def deauthenticate_user(request):
    """
    Desautentifica al usuario relacionado con la sesión de la solicitud.

    :param request: Los datos de la solicitud.

    :returns: Un *HttpResponseRedirect* a la página de logeo.
    """
    #TODO On logout, redirect to login?
    djLogout(request)
    return HttpResponseRedirect(reverse(base_settings.LOGIN_NAME))


def perfil(request, user_id):
    """
    Retorna la vista correspondiente al perfil de un usuario

    :param request: Los datos de la solicitud

    :returns: Un 'renderizado' del template profile_detail.

    """

    if not(request.user.is_active):
        return HttpResponseRedirect(reverse(base_settings.LOGIN_NAME))

    from django.shortcuts import get_object_or_404
    from apps.autenticacion.models import User

    profile_user = get_object_or_404(User, id=user_id)


    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'user_projects' : [],
        'left_active': 'Visualizar',
        'profile_user': profile_user
    }

    for p in profile_user.get_projects():
        if request.user.user.id != user_id:
            active_user_perms = p[0].get_user_perms(request.user.user)
            if len(active_user_perms) == 0:
                continue

        names = [r.desc_larga for r in p[1]]
        context['user_projects'].append((p[0], ', '.join(names)))

    x = UserPermissionContextMixin()
    x.request = request
    x.get_user_permissions(context)


    return render(request, 'autenticacion/profile_detail', context)

def profile_projects(request):
    """
    Retorna la vista correspondiente a la lista de proyectos del usuario activo
    """
    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'user_projects': [],
        'left_active': 'Mis Proyectos',
        'section_title': 'Mis Proyectos'
    }

    for p in request.user.user.get_projects():
        names = [r.desc_larga for r in p[1]]
        context['user_projects'].append((p[0], ', '.join(names)))

    x = UserPermissionContextMixin()
    x.request = request
    x.get_user_permissions(context)

    return render(request, 'autenticacion/profile_project_list', context)

