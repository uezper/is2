from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from scrunban.settings.base import LOGIN_NAME, PERFIL_NAME
from django.http.response import HttpResponseRedirect


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

class UserIsAuthenticatedMixin(LoginRequiredMixin):
    login_url = reverse_lazy(LOGIN_NAME)
    redirect_field_name = None


class ValidateTestMixin(object):
    """

    Mixin que permita la validacion de ciertos test antes de ingresar a una vista

    """

    def get_redirect_url(self, request, *args, **kwargs):
        return reverse_lazy(PERFIL_NAME, args=[request.user.user.id])

    def validate_tests(self, request, *args, **kwargs):
        return True

    def dispatch(self, request, *args, **kwargs):
        if not self.validate_tests(request, *args, **kwargs):
            return HttpResponseRedirect(self.get_redirect_url(request, *args, **kwargs))

        return super(ValidateTestMixin, self).dispatch(request, *args, **kwargs)




