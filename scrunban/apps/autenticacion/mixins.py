
class UserPermissionContextMixin(object):
    """

        Mixin utilizado para agregar la lista de permisos del usuarios al context

        :param user_permission_context_name: Nombre que sera utilizado dentro del context para guardar los datos
    """
    user_permission_context_name = 'user_permissions'

    def get_user_permissions(self, context):
        context[self.user_permission_context_name] = {}
        for perm in self.request.user.user.get_all_permissions():
            context[self.user_permission_context_name][perm] = True
