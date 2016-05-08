from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin

from apps.autenticacion.models import Role
from apps.administracion.models import Project
from apps.proyecto.models import Team, Sprint

from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES
from apps.proyecto import forms
from django.shortcuts import get_object_or_404, HttpResponseRedirect

from apps.proyecto.mixins import PermissionListMixin, UrlNamesContextMixin, UserListMixin, ValidateSprintState
from apps.autenticacion.mixins import UserPermissionContextMixin, UserIsAuthenticatedMixin
from scrunban.settings import base as base_settings

from django.shortcuts import render

class RoleListView(UserIsAuthenticatedMixin, ListView, SingleObjectMixin, UrlNamesContextMixin, UserPermissionContextMixin):

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

class RoleCreateView(UserIsAuthenticatedMixin, FormView, SingleObjectMixin, UrlNamesContextMixin, UserListMixin, PermissionListMixin, UserPermissionContextMixin):
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








class DevListView(UserIsAuthenticatedMixin, ListView, SingleObjectMixin, UrlNamesContextMixin, UserPermissionContextMixin):

    """
    Clase correspondiente a la vista que lista los desarrolladores de un proyecto


    """
    model = Team
    context_object_name = 'dev_list'
    template_name = 'proyecto/project_dev_team_list'

    pk_url_kwarg = 'project_id'

    paginate_by = 10

    section_title = 'Equipo de Desarrollo'
    left_active = 'Equipo de Desarrollo'

    def get_queryset(self):
        self.object = self.get_object(queryset=Project.objects.all())
        return Team.teams.filter(project=self.object)

    def get_context_data(self, **kwargs):
        context = super(DevListView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions(context)

        context['project'] = self.object

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active


        return context



class DevEditView(UserIsAuthenticatedMixin, FormView, SingleObjectMixin, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite editar la cantidad de hs-hombre de un usuario dentro de un proyecto

    """

    form_class = forms.EditDevForm

    section_title = 'Editar Cantidad de Horas Hombre'

    team_id_kwname = 'team_id'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'
    template_name = 'proyecto/project_dev_team_edit'
    left_active = 'Equipo de Desarrollo'


    def get_initial(self):
        team_id = self.kwargs.get(self.team_id_kwname)
        team = get_object_or_404(Team, id=team_id)

        initial = {
            'id': team.id,
            'username': team.user.get_first_name() + ' ' + team.user.get_last_name(),
            'hs_hombre': team.hs_hombre
        }


        return initial

    def post(self, request, *args, **kwargs):
        from django.http.request import QueryDict

        team_id = self.kwargs.get(self.team_id_kwname)
        team = get_object_or_404(Team, id=team_id)

        form_class = self.get_form_class()

        data = QueryDict.dict(request.POST)

        data.update({
            'id': team.id
        })

        qdict = QueryDict('', mutable=True)
        qdict.update(data)

        form = form_class(qdict)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        self.object = self.get_object(queryset=Project.objects.all())

        context = super(DevEditView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions(context)

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active


        return context

    def get_success_url(self):
        project = self.get_object(queryset=Project.objects.all())

        from scrunban.settings.base import PROJECT_DEV_LIST
        return reverse(PROJECT_DEV_LIST, args=(project.id,))


    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):

        context = {
            'form': form
        }
        print(form)

        return super(DevEditView, self).render_to_response(self.get_context_data(**context))


class SprintListView(UserIsAuthenticatedMixin, ListView, SingleObjectMixin, UrlNamesContextMixin, UserPermissionContextMixin):

    """
    Clase correspondiente a la vista que lista los Sprints de un proyecto


    """
    model = Sprint
    context_object_name = 'sprint_list'
    template_name = 'proyecto/project_sprint_list'

    pk_url_kwarg = 'project_id'

    paginate_by = 10

    section_title = 'Sprints'
    left_active = 'Sprints'


    def get_queryset(self):
        self.object = self.get_object(queryset=Project.objects.all())
        return Sprint.sprints.filter(project=self.object)

    def get_context_data(self, **kwargs):
        context = super(SprintListView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions(context)

        context['project'] = self.object

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active


        return context


class SprintCreateView(UserIsAuthenticatedMixin, FormView, SingleObjectMixin, UrlNamesContextMixin, UserPermissionContextMixin):
    """
    Clase correspondiente a la vista que permite crear un Sprint dentro de un proyecto

    """

    form_class = forms.CreateSprintForm
    template_name = 'proyecto/project_sprint_create'

    context_object_name = 'project'

    pk_url_kwarg = 'project_id'

    section_title = 'Crear Sprint'
    left_active = 'Sprints'


    def get_default_fields(self):
        project = self.get_object(queryset=Project.objects.all())

        data = {
            'project': project.id
        }

        return data

    def post(self, request, *args, **kwargs):
        from django.http.request import QueryDict

        form_class = self.get_form_class()

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

        self.object = self.get_object(queryset=Project.objects.all())

        context = super(SprintCreateView, self).get_context_data(**kwargs)

        self.get_url_context(context)
        self.get_user_permissions(context)

        context['section_title'] = self.section_title
        context['left_active'] = self.left_active

        return context

    def get_success_url(self):
        project = self.get_object(queryset=Project.objects.all())

        from scrunban.settings.base import PROJECT_SPRINT_LIST
        return reverse(PROJECT_SPRINT_LIST, args=(project.id,))

    def get_initial(self):
        from apps.proyecto.models import Sprint
        project = self.get_object(queryset=Project.objects.all())
        sec = 0
        sprints = Sprint.objects.filter(project=project)

        if sprints.count() != 0:
            sec = sprints.last().sec + 1


        initial = {
            'sec': 'Sprint ' + str(sec)
        }

        return initial

    def form_valid(self, form):

        form.save()
        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):

        context = {
            'form' : form
        }

        return super(SprintCreateView, self).render_to_response(self.get_context_data(**context))



class SprintEditView(ValidateSprintState, SprintCreateView):
    """
    Clase correspondiente a la vista que permite editar un Sprint dentro de un proyecto

    """

    form_class = forms.EditSprintForm

    sprint_url_kwarg = 'sprint_id'

    section_title = 'Editar Sprint'


    def get_default_fields(self):
        from apps.proyecto.models import Sprint

        project = self.get_object(queryset=Project.objects.all())
        sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg))

        data = {
            'project': project.id,
            'id': sprint.id
        }

        return data

    def get_context_data(self, **kwargs):
        context = super(SprintEditView, self).get_context_data(**kwargs)
        context['edit_form'] = True

        return context

    def get_initial(self):
        from apps.proyecto.models import Sprint
        sprint = get_object_or_404(Sprint, id=self.kwargs.get(self.sprint_url_kwarg))

        initial = {
            'sec': sprint.sec,
            'estimated_time': sprint.get_estimated_time()
        }

        return initial