from scrunban.settings.base import URL_NAMES, PROJECT_SPRINT_LIST
from apps.autenticacion.models import User
from apps.autenticacion.mixins import ValidateTestMixin
from django.core.urlresolvers import reverse

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
        return User.objects.all()

class ValidateSprintStatePending(ValidateTestMixin):
    """
    Mixin que valida que el estado de un Sprint sea Pendiente antes de entrar en una vista
    """

    def get_fail_state_url(self, request, *args, **kwargs):
        from apps.administracion.models import Project
        from django.shortcuts import get_object_or_404

        project = get_object_or_404(Project, id=kwargs.get(self.pk_url_kwarg))

        return reverse(PROJECT_SPRINT_LIST, args=(project.id,))

    def validate_tests(self, request, *args, **kwargs):

        sup = super(ValidateSprintStatePending, self).validate_tests(request, *args, **kwargs)

        from apps.proyecto.models import Sprint
        from django.shortcuts import get_object_or_404

        sprint = get_object_or_404(Sprint, id=kwargs.get(self.sprint_url_kwarg))

        if sprint.get_state() == Sprint.state_choices[0][0]:
            return sup

        return self.get_fail_state_url(request, *args, **kwargs)