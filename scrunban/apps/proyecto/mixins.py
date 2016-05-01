from scrunban.settings.base import URL_NAMES
from apps.autenticacion.models import User

class UrlNamesContextMixin(object):

    url_names_context_name = 'URL_NAMES'

    def get_url_context(self, context):

        context[self.url_names_context_name] = URL_NAMES

class PermissionListMixin(object):

    permission_list_context_name = 'perm_list'

    def get_permission_list_context(self, context):

        from django.contrib.auth.models import Permission
        context[self.permission_list_context_name] = Permission.objects.filter(codename__startswith='project_')

class UserListMixin(object):

    user_list_context_name = 'user_list'

    def get_user_list_context(self, context):

        context[self.user_list_context_name] = self.get_user_list_queryset()

    def get_user_list_queryset(self):
        return User.objects.all()

