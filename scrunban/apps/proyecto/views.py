from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from apps.autenticacion.models import Role
from apps.administracion.models import Project

from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES
from apps.proyecto import forms
from django.shortcuts import get_object_or_404, HttpResponseRedirect

from apps.proyecto.mixins import PermissionListMixin, UrlNamesContextMixin, UserListMixin
from apps.autenticacion.mixins import UserPermissionContextMixin

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from scrunban.settings import base as base_settings

from django.shortcuts import render

class RoleListView(ListView, SingleObjectMixin, UrlNamesContextMixin, UserPermissionContextMixin):

    """
    Clase correspondiente a la vista que lista los roles de un proyecto


    """
    model = Role
    context_object_name = 'role_list'
    template_name = 'proyecto/role_list'

    pk_url_kwarg = 'project_id'

    paginate_by = 10

    section_title = 'Lista de Roles'
    left_active = 'Roles'

    @method_decorator(login_required(login_url=base_settings.LOGIN_NAME))
    def dispatch(self, *args, **kwargs):
        return super(RoleListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.object = self.get_object(queryset=Project.objects.all())
        return self.object.get_roles()

    def get_context_data(self, **kwargs):
        context = super(RoleListView, self).get_context_data(**kwargs)

        self.get_role_info(context)
        self.get_url_context(context)
        self.get_user_permissions(context)

        context['project'] = self.object

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active


        return context

    def get_role_info(self, context):

        role_list = context[self.context_object_name]
        new_role_list = []

        for rol in role_list:
            removable = True
            users = len(rol.group.user_set.all())


            for default_rol in DEFAULT_PROJECT_ROLES:
                if (str(self.object.id) + '_' + default_rol[0] == rol.group.name):
                    removable = False
                    break


            new_role_list.append((rol, removable, users))

        context[self.context_object_name] = new_role_list

class RoleCreateView(FormView, SingleObjectMixin, UrlNamesContextMixin, UserListMixin, PermissionListMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite crear un rol dentro de un proyecto

    """

    form_class = forms.CreateRolForm
    template_name = 'proyecto/role_crud'

    context_object_name = 'project'

    pk_url_kwarg = 'project_id'

    section_title = 'Crear Rol'
    left_active = 'Roles'

    @method_decorator(login_required(login_url=base_settings.LOGIN_NAME))
    def dispatch(self, *args, **kwargs):
        return super(RoleCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        self.object = self.get_object(queryset=Project.objects.all())

        context = super(RoleCreateView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_list_context(context)
        self.get_permission_list_context(context)
        self.get_user_permissions(context)


        context['section_title'] = self.section_title
        context['left_active'] = self.left_active

        return context

    def get_success_url(self):
        project = self.get_object(queryset=Project.objects.all())

        from scrunban.settings.base import PROJECT_ROLE_LIST
        return reverse(PROJECT_ROLE_LIST, args=(project.id,))

    def get_initial(self):
        project = self.get_object(queryset=Project.objects.all())

        initial = {
            'projectID': project.id,
        }

        return initial

    def form_valid(self, form):

        form.save()
        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):

        form_data = {
            'inputPerms': form.data.get('inputPerms',''),
            'inputUsers': form.data.get('inputUsers',''),
            'inputNombre': form.data.get('inputNombre',''),
        }

        context = {
            'form_data' : form_data,
            'form' : form
        }

        return super(RoleCreateView, self).render_to_response(self.get_context_data(**context))

class RoleEditView(RoleCreateView):
    """
    Clase correspondiente a la vista que permite editar un rol dentro de un proyecto

    """

    form_class = forms.EditRolForm

    section_title = 'Editar Rol'

    rol_id_kwname = 'rol_id'

    def get_initial(self):
        project = self.get_object(queryset=Project.objects.all())
        rol_id = self.kwargs.get(self.rol_id_kwname)
        rol = get_object_or_404(Role, id=rol_id)

        p_list = [perm.codename for perm in rol.get_perms()]
        u_list = [str(user.user.id) for user in rol.group.user_set.all()]

        initial = {
            'projectID': project.id,
            'inputPerms': ','.join(p_list),
            'inputUsers': ','.join(u_list),
            'inputNombre': rol.get_desc(),
            'inputOldNombre': rol.get_desc(),
        }

        return initial


    def get_context_data(self, **kwargs):

        context = super(RoleEditView, self).get_context_data(**kwargs)

        project_id = self.kwargs.get(self.pk_url_kwarg)
        rol_id = self.kwargs.get(self.rol_id_kwname)
        rol = get_object_or_404(Role, id=rol_id)

        context['rol'] = rol

        for r in DEFAULT_PROJECT_ROLES:
            if str(project_id) + '_' + r[0] == rol.get_name():
                context['not_editable_perms'] = True
                break

        context['edit_form'] = True



        return context

class RoleDeleteView(RoleEditView):
    """
    Clase correspondiente a la vista que permite eliminar un rol dentro de un proyecto

    """


    form_class = forms.DeleteRolForm

    section_title = 'Borrar Rol'

    def get(self, request, *args, **kwargs):
        form = self.form_class(self.get_initial())
        if (form.is_valid()):
            return super(RoleDeleteView, self).get(request, *args, **kwargs)
        else:
            from scrunban.settings.base import PROJECT_ROLE_LIST

            project = self.get_object(queryset=Project.objects.all())

            return HttpResponseRedirect(reverse(PROJECT_ROLE_LIST, args=(project.id,)))

    def get_initial(self):
        initial = super(RoleDeleteView, self).get_initial()
        initial['inputID'] = self.kwargs.get(self.rol_id_kwname)


        return initial

    def get_context_data(self, **kwargs):

        context = super(RoleDeleteView, self).get_context_data(**kwargs)

        context['no_editable'] = True
        context['delete_form'] = True

        return context

def index(request, project_id):

    context = {
        'URL_NAMES': base_settings.URL_NAMES,
        'project' : get_object_or_404(Project, id=project_id)
    }

    return render(request, 'proyecto/project_index', context)