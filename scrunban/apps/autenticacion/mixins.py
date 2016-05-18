from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from scrunban.settings.base import LOGIN_NAME, PERFIL_NAME
from django.http.response import HttpResponseRedirect


class UserPermissionListMixin(object):
    """
        Mixin que se encarga de crear una lista de todos los permisos de usuario (de proyecto y sistema)
    """

    def get_project(self):
        return None

    def get_user_permissions_list(self):
        from apps.autenticacion.models import Role
        from apps.autenticacion.settings import DEF_ROLE_ADMIN

        r = Role.objects.get(group__name=DEF_ROLE_ADMIN[0])


        result = []

        # Permisos de un proyecto especifico
        project = self.get_project()
        if (project != None):
            for perm in project.get_user_perms(self.request.user.user):
                result.append(perm)

        # Permisos globales (rol administrativo)
        if self.request.user.user in r.get_users():
            for perm in r.get_perms():
                result.append(perm)

        return result


class UserPermissionContextMixin(UserPermissionListMixin):
    """

        Mixin utilizado para agregar la lista de permisos del usuarios al context

        :param user_permission_context_name: Nombre que sera utilizado dentro del context para guardar los datos
    """
    user_permission_context_name = 'user_permissions'


    def get_user_permissions_context(self, context):
        context[self.user_permission_context_name] = {}

        for perm in self.get_user_permissions_list():
            context[self.user_permission_context_name][perm.codename] = True



class UserIsAuthenticatedMixin(LoginRequiredMixin):
    login_url = reverse_lazy(LOGIN_NAME)
    redirect_field_name = None


class ValidateTestMixin(object):
    """

    Mixin que permita la validacion de ciertos test antes de ingresar a una vista

    """


    def validate_tests(self, request, *args, **kwargs):
        return None

    def dispatch(self, request, *args, **kwargs):

        x = self.validate_tests(request, *args, **kwargs)
        if x != None:
            return HttpResponseRedirect(x)

        return super(ValidateTestMixin, self).dispatch(request, *args, **kwargs)


class ValidateHasPermission(ValidateTestMixin, UserPermissionListMixin):
    """

    Mixin que permite verificar si un usuario tiene un determinado permiso para entrar en una vista

    """

    def get_required_permissions(self):
        return []

    def get_fail_permission_url(self, request, *args, **kwargs):
        return reverse_lazy(PERFIL_NAME, args=[request.user.user.id])

    def validate_tests(self, request, *args, **kwargs):

        sup = super(ValidateHasPermission, self).validate_tests(request, *args, **kwargs)

        user_perms = self.get_user_permissions_list()

        required = self.get_required_permissions()

        if len(required) == 0:
            return sup

        for perm in required:
            if perm in user_perms:
                return sup

        return self.get_fail_permission_url(request, *args, **kwargs)







