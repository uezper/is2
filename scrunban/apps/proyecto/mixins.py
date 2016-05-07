from scrunban.settings.base import URL_NAMES
from apps.autenticacion.models import User

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


