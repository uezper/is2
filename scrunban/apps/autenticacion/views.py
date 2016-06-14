import json, logging
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate as djAuthenticate
from django.contrib.auth import login as djLogin
from django.contrib.auth import logout as djLogout

from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView

from apps.administracion.forms import UserEditForm
from django.shortcuts import HttpResponseRedirect

from apps.proyecto.mixins import UrlNamesContextMixin, ValidateSprintState
from apps.autenticacion.mixins import UserPermissionContextMixin, UserIsAuthenticatedMixin
from scrunban.settings import base as base_settings

# Define loggers
stdlogger = logging.getLogger(base_settings.LOGGERS_NAME['administracion'])

# Define log entries formatters
def formatter(action, actor):
    return '{} has {}'.format(actor, action)

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

                    # Log event
                    kwargs = {
                        'action': 'log in',
                        'actor': request.user.get_full_name()
                    }
                    stdlogger.info(formatter(**kwargs))
                    
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
    # Log event
    kwargs = {
        'action': 'log out',
        'actor': request.user.get_full_name()
    }
    stdlogger.info(formatter(**kwargs))
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
    from apps.autenticacion.settings import ADMIN_USER_MANAGEMENT
    from apps.autenticacion.mixins import UserPermissionListMixin

    profile_user = get_object_or_404(User, id=user_id)

    pml = UserPermissionListMixin()
    pml.request = request
    permissions = [p.codename for p in pml.get_user_permissions_list()]


    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'user_projects' : [],
        'left_active': 'Visualizar',
        'profile_user': profile_user
    }

    for p in profile_user.get_projects():
        if request.user.user.id != user_id and not(ADMIN_USER_MANAGEMENT[0] in permissions):
            active_user_perms = p[0].get_user_perms(request.user.user)
            if len(active_user_perms) == 0:
                continue

        names = [r.desc_larga for r in p[1]]
        context['user_projects'].append((p[0], ', '.join(names)))

    x = UserPermissionContextMixin()
    x.request = request
    x.get_user_permissions_context(context)


    return render(request, 'autenticacion/profile_detail', context)
import datetime
def profile_projects(request):
    """
    Retorna la vista correspondiente a la lista de proyectos del usuario activo
    """
    print(datetime.datetime.now().date())
    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'user_projects': [],
        'left_active': 'Mis Proyectos',
        'section_title': 'Mis Proyectos',
        'date_now': datetime.datetime.now().date()
    }

    for p in request.user.user.get_projects():
        names = [r.desc_larga for r in p[1]]
        context['user_projects'].append((p[0], ', '.join(names)))

    x = UserPermissionContextMixin()
    x.request = request
    x.get_user_permissions_context(context)

    return render(request, 'autenticacion/profile_project_list', context)



class ProfileEditView(UserIsAuthenticatedMixin, FormView, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite editar el perfil

    """

    form_class = UserEditForm
    template_name = 'autenticacion/profile_edit'

    section_title = 'Editar perfil'
    left_active = 'Editar perfil'

    def get_default_fields(self):
        data = {
            'id': self.request.user.user.id
        }

        return data

    def post(self, request, *args, **kwargs):
        from django.http.request import QueryDict

        form_class = self.get_form_class()

        # Recibe la peticion enviada por POST
        # y actualiza agregando los campos por defecto basados en la vista
        data = QueryDict.dict(request.POST)

        data.update(**self.get_default_fields())

        qdict = QueryDict('', mutable=True)
        qdict.update(data)

        form = form_class(qdict)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):

        context = super(ProfileEditView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions_context(context)

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active
        context['edit_form'] = True

        return context

    def get_success_url(self):
        from scrunban.settings.base import PERFIL_NAME
        return reverse(PERFIL_NAME, args=(self.request.user.user.id,))

    def get_initial(self):
        from apps.autenticacion.models import User
        user = User.objects.get(id=self.request.user.user.id)


        initial = {
            'username': user.get_username(),
            'telefono': user.get_telefono(),
            'first_name': user.get_first_name(),
            'last_name': user.get_last_name(),
            'direccion': user.get_direccion(),
            'email': user.get_email(),
        }

        return initial

    def form_valid(self, form):

        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):

        context = {
            'form': form
        }

        return super(ProfileEditView, self).render_to_response(self.get_context_data(**context))
