from scrunban.settings.base import URL_NAMES, PROJECT_SPRINT_LIST
from apps.autenticacion.models import User
from apps.autenticacion.mixins import ValidateTestMixin, UserIsAuthenticatedMixin, UserPermissionContextMixin, ValidateHasPermission
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

class UrlNamesContextMixin(object):
    """
        Mixin utilizado para cargar los nombres de la los urls del sistema dentro del context

        :param url_names_context_name: Nombre que sera utilizado dentro del context para guardar los datos

    """
    url_names_context_name = 'URL_NAMES'

    def get_url_context(self, context):
        """
        Agrega la lista de nombres de url al context

        :param context: Context de la vista
        """
        context[self.url_names_context_name] = URL_NAMES

class PermissionListMixin(object):
    """

    Mixin utilizado para agregar la lista de permisos del sistema al context

    :param permission_list_context_name: Nombre que sera utilizado dentro del context para guardar los datos
    """

    permission_list_context_name = 'perm_list'

    def get_permission_list_context(self, context):
        """
            Agrega la lista de permisos al context

            :param context: Context de la vista
         """
        from django.contrib.auth.models import Permission
        context[self.permission_list_context_name] = Permission.objects.filter(codename__startswith='project_')

class UserListMixin(object):
    """

        Mixin utilizado para agregar una lista de usuarios al context

        :param user_list_context_name: Nombre que sera utilizado dentro del context para guardar los datos
    """

    user_list_context_name = 'user_list'

    def get_user_list_context(self, context):
        """
            Agrega la lista de usuarios al context

            :param context: Context de la vista
        """
        context[self.user_list_context_name] = self.get_user_list_queryset()

    def get_user_list_queryset(self):
        """
           Metodo que devuelve el queryset del cual se listaran los usuarios

            :returns: Queryset
        """

        res = []

        for u in User.objects.all():
            if u.user.is_active:
                res.append(u)

        return res

class ValidateSprintState(ValidateTestMixin):
    """
    Mixin que valida que el estado de un Sprint no sea el de finalizado o cancelado antes de entrar en una vista
    """

    def get_fail_state_url(self, request, *args, **kwargs):
        from apps.administracion.models import Project
        from django.shortcuts import get_object_or_404

        project = get_object_or_404(Project, id=kwargs.get(self.pk_url_kwarg))

        return reverse(PROJECT_SPRINT_LIST, args=(project.id,))

    def validate_tests(self, request, *args, **kwargs):

        sup = super(ValidateSprintState, self).validate_tests(request, *args, **kwargs)

        from apps.proyecto.models import Sprint
        from django.shortcuts import get_object_or_404

        sprint = get_object_or_404(Sprint, id=kwargs.get(self.sprint_url_kwarg))

        if sprint.get_state() in ['Pendiente', 'Ejecucion']:
            return sup

        return self.get_fail_state_url(request, *args, **kwargs)


class DefaultFormDataMixin(object):

    def get_default_fields(self):
        return {}

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

class ProjectViwMixin(UserIsAuthenticatedMixin, ValidateHasPermission, UrlNamesContextMixin, UserPermissionContextMixin):

    __checked = False


    def get_fail_permission_url(self, request, *args, **kwargs):
        from scrunban.settings.base import PROJECT_INDEX
        project = self.get_project()

        return reverse(PROJECT_INDEX, args=(project.id,))


    def get_project(self):
        from apps.proyecto.models import Project
        from datetime import datetime
        project_id = self.kwargs.get(self.pk_url_kwarg, None)
        project = get_object_or_404(Project, id=project_id)

        if not(self.__checked):
            from apps.proyecto.models import Sprint
            from apps.administracion.models import Grained

            self.__checked = True

            sprints = Sprint.objects.filter(project=project, state='Ejecucion')
            for s in sprints:
                print(((datetime.now(s.start_date.tzinfo) - s.start_date).days))
                if (datetime.now(s.start_date.tzinfo) - s.start_date).days >= s.estimated_time:
                    s.state = 'Finalizado'
                    s.save()

                    for g in Grained.objects.filter(sprint=s):
                        x = g.user_story
                        x.delay_urgency = x.delay_urgency + 2
                        x.save()



        return project

    def get_context_data(self, **kwargs):
        context = super(ProjectViwMixin, self).get_context_data(**kwargs)
        context['project'] = self.get_project()
        context['section_title'] = self.section_title
        context['left_active'] = self.left_active

        self.get_url_context(context)
        self.get_user_permissions_context(context)


        return context


