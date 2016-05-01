import json
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate as djAuthenticate
from django.contrib.auth import login as djLogin
from django.contrib.auth import logout as djLogout
from scrunban.settings import base as base_settings
from apps.autenticacion.decorators import login_required


#TODO! Cambiar cuando este la nueva app
from apps.administracion.models import Project
from django.shortcuts import get_object_or_404, HttpResponse
from apps.autenticacion import settings as role_settings
from django.contrib.auth.models import Permission
from apps.autenticacion.models import User, Role

def login(request):
    """
    Retorna la vista correspondiente a la página de login.

    :param request: Los datos de la solicitud

    :returns: Un 'renderizado' del template correspondiente.
    """
    
    if request.user.is_active:
        return HttpResponseRedirect(reverse(base_settings.PERFIL_NAME))

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

@login_required(base_settings.PERFIL_NAME)
def perfil(request):
    """
    Retorna la vista correspondiente al perfil del usuario

    :param request: Los datos de la solicitud

    :returns: Un 'renderizado' del template perfil.

    """


    context = {
        'URL_NAMES': base_settings.URL_NAMES,
    }

    return render(request, 'autenticacion/perfil', context)

# TODO! Cambiar esto cuando este la nueva app

def role_list(request, project_id):
    """
    Retorna la vista correspondiente a la lista de roles de projecto

    :para project_id: Id del Proyecto
    :param request: Los datos de la solicitud


    """

    project = get_object_or_404(Project, id=project_id)

    role_list = project.get_roles()

    new_role_list = []
    for rol in role_list:
        removable = True
        users = len(rol.group.user_set.all())

        #if (users > 0):
        #    removable = False

        for def_rol in role_settings.DEFAULT_PROJECT_ROLES:
            if (str(project_id) + '_' + def_rol[0] == rol.group.name):
                removable = False
                break

        new_role_list.append((rol, removable, users))

    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'role_list' : new_role_list,
        'project' : project,
    }
    return render(request, 'autenticacion/role_list', context)


def rol_detail(request, project_id, rol_id):
    """
        Retorna la vista correspondiente a los detalles de un rol de proyecto

        :para project_id: Id del Proyecto
        :param rol_id: Id del rol
        :param request: Los datos de la solicitud


    """

    project = get_object_or_404(Project, id=project_id)
    rol = get_object_or_404(Role, id=rol_id)

    p_list = [perm.codename for perm in rol.get_perms()]
    u_list = [str(user.user.id) for user in rol.group.user_set.all()]

    data = {
        'projectID' : project_id,
        'inputPerms' : ','.join(p_list),
        'inputUsers' : ','.join(u_list),
        'inputNombre' : rol.get_desc(),
        'inputID' : rol_id
    }

    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project': project,
    }

    perm_list = Permission.objects.filter(codename__startswith='project_')
    user_list = User.objects.all()

    context['form_data'] = {
        'inputPerms': data['inputPerms'],
        'inputUsers': data['inputUsers'],
        'inputNombre': data['inputNombre'],
    }

    context['rol_id'] = rol_id
    context['section_title'] = 'Visualizar rol'
    context['no_editable'] = True
    context['detail_form'] = True
    context['user_list'] = user_list
    context['perm_list'] = perm_list

    return render(request, 'autenticacion/role_create_delete', context)

def rol_delete(request, project_id, rol_id):
    """
        Retorna la vista correspondiente a la eliminacion de un rol de proyecto

        :para project_id: Id del Proyecto
        :param rol_id: Id del rol
        :param request: Los datos de la solicitud


    """
    from .forms import DeleteRolForm as f

    project = get_object_or_404(Project, id=project_id)
    rol = get_object_or_404(Role, id=rol_id)


    p_list = [perm.codename for perm in rol.get_perms()]
    u_list = [str(user.user.id) for user in rol.group.user_set.all()]

    data = {
        'projectID' : project_id,
        'inputPerms' : ','.join(p_list),
        'inputUsers' : ','.join(u_list),
        'inputNombre' : rol.get_desc(),
        'inputID' : rol_id
    }

    form = f(data)

    context = {
        'URL_NAMES' : base_settings.URL_NAMES,
        'project': project,
    }

    if (request.method == "POST"):
        form = f(request.POST)
        if (form.is_valid()):
            rol = form.cleaned_data['inputID']

            project.remove_rol(short_name=rol.get_name())

            return HttpResponseRedirect(reverse(base_settings.PROJECT_ROLE_LIST, args=(project_id,)))

    else:

        from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES

        for r in DEFAULT_PROJECT_ROLES:
            if str(project_id) + '_' + r[0] == rol.get_name():
                return HttpResponseRedirect(reverse(base_settings.PROJECT_ROLE_LIST, args=(project_id,)))


    perm_list = Permission.objects.filter(codename__startswith='project_')
    user_list = User.objects.all()

    context['form_data'] = {
        'inputPerms': form.data['inputPerms'],
        'inputUsers': form.data['inputUsers'],
        'inputNombre': form.data['inputNombre'],
    }

    context['rol_id'] = rol_id
    context['section_title'] = 'Borrar rol'
    context['delete_id'] = rol_id
    context['no_editable'] = True
    context['delete_form'] = True
    context['user_list'] = user_list
    context['perm_list'] = perm_list
    context['form'] = form

    return render(request, 'autenticacion/role_create_delete', context)



def role_create(request, project_id):
    """
        Retorna la vista correspondiente a la creacion de un rol de proyecto

        :para project_id: Id del Proyecto
        :param rol_id: Id del rol
        :param request: Los datos de la solicitud


    """
    from .forms import CreateRolForm as f
    form = f()

    project = get_object_or_404(Project, id=project_id)


    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project': project,
    }

    if (request.method == "POST"):
            form = f(request.POST)
            if (form.is_valid()):
                perms = form.cleaned_data['inputPerms']
                users = form.cleaned_data['inputUsers']
                rol_name = form.cleaned_data['inputNombre']

                rol = project.add_rol(desc_larga=rol_name)

                for p in perms:
                    rol.add_perm(p)

                for u in users:
                    rol.add_user(u)

                return HttpResponseRedirect(reverse(base_settings.PROJECT_ROLE_LIST, args=(project_id,)))
            else:
                context['form_data'] = {
                    'inputPerms' : form.data['inputPerms'],
                    'inputUsers': form.data['inputUsers'],
                    'inputNombre': form.data['inputNombre'],
                }


    perm_list = Permission.objects.filter(codename__startswith='project_')
    user_list = User.objects.all()

    context['section_title'] = 'Crear rol'
    context['user_list'] = user_list
    context['perm_list'] = perm_list
    context['form'] = form


    return render(request, 'autenticacion/role_create_delete', context)



def role_edit(request, project_id, rol_id):

    from .forms import EditRolForm as f

    project = get_object_or_404(Project, id=project_id)
    rol = get_object_or_404(Role, id=rol_id)

    p_list = [perm.codename for perm in rol.get_perms()]
    u_list = [str(user.user.id) for user in rol.group.user_set.all()]

    data = {
        'projectID': project_id,
        'inputPerms': ','.join(p_list),
        'inputUsers': ','.join(u_list),
        'inputNombre': rol.get_desc(),
        'inputOldNombre': rol.get_desc(),
    }

    form = f(data)



    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project': project,
    }

    if (request.method == "POST"):
            form = f(request.POST)
            if (form.is_valid()):

                perms = form.cleaned_data['inputPerms']
                users = form.cleaned_data['inputUsers']

                print(users)

                rol = Role.objects.filter(id=rol_id)[0]

                rol.set_desc(form.cleaned_data['inputNombre'])

                for p in rol.group.permissions.all():
                    rol.remove_perm(p)

                for u in rol.group.user_set.all():
                    rol.remove_user(u.user)

                for p in perms:
                    rol.add_perm(p)

                for u in users:
                    rol.add_user(u)

                print(rol.group.user_set.all())

                return HttpResponseRedirect(reverse(base_settings.PROJECT_ROLE_LIST, args=(project_id,)))


    context['form_data'] = {
        'inputPerms' : form.data['inputPerms'],
        'inputUsers': form.data['inputUsers'],
        'inputNombre': form.data['inputNombre'],
    }


    from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES

    for r in DEFAULT_PROJECT_ROLES:
        if str(project_id) + '_' + r[0] == rol.get_name():
            context['not_editable_perms'] = True
            break

    perm_list = Permission.objects.filter(codename__startswith='project_')
    user_list = User.objects.all()

    context['rol_id'] = rol_id
    context['edit_old_name'] = form.data['inputOldNombre']
    context['edit_form'] = True
    context['section_title'] = 'Editar rol'
    context['user_list'] = user_list
    context['perm_list'] = perm_list
    context['form'] = form


    return render(request, 'autenticacion/role_create_delete', context)