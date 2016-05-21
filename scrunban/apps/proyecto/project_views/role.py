from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, FormView
from apps.proyecto.mixins import ProjectViwMixin, UserListMixin, PermissionListMixin
from apps.proyecto import forms
from apps.proyecto.models import Role

class RoleListView(ProjectViwMixin, ListView):

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

    def get_queryset(self):
        project = self.get_project()
        return project.get_roles()

    def get_context_data(self, **kwargs):
        context = super(RoleListView, self).get_context_data(**kwargs)

        self.get_role_info(context)

        return context

    def get_role_info(self, context):

        from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES

        project = self.get_project()
        role_list = context[self.context_object_name]
        new_role_list = []

        for rol in role_list:
            removable = True
            users = len(rol.group.user_set.all())


            for default_rol in DEFAULT_PROJECT_ROLES:
                if (str(project.id) + '_' + default_rol[0] == rol.group.name):
                    removable = False
                    break


            new_role_list.append((rol, removable, users))

        context[self.context_object_name] = new_role_list

class RoleCreateView(ProjectViwMixin, FormView, UserListMixin, PermissionListMixin):
    """
    Clase correspondiente a la vista que permite crear un rol dentro de un proyecto

    """

    form_class = forms.CreateRolForm
    template_name = 'proyecto/role_crud'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'
    section_title = 'Crear Rol'
    left_active = 'Roles'

    def get_context_data(self, **kwargs):

        context = super(RoleCreateView, self).get_context_data(**kwargs)

        self.get_user_list_context(context)
        self.get_permission_list_context(context)


        context['section_title'] = self.section_title
        context['left_active'] = self.left_active

        return context


    def get_success_url(self):
        project = self.get_project()

        from scrunban.settings.base import PROJECT_ROLE_LIST
        return reverse(PROJECT_ROLE_LIST, args=(project.id,))

    def get_initial(self):
        project = self.get_project()

        initial = {
            'projectID': project.id,
        }

        return initial

    def form_valid(self, form):

        form.save()
        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):

        context = {
            'form': form
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
        project = self.get_project()
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

        from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES

        context = super(RoleEditView, self).get_context_data(**kwargs)

        project = self.get_project()
        project_id = project.id
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

            project = self.get_project()

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