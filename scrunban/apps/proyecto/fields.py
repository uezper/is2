from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from apps.autenticacion.models import User


class StringListField(forms.CharField):

    def to_python(self, value):
        if value in [None, '', [], ()]:
            return []

        return value.split(',')


class PermissionListField(StringListField):
    default_error_messages = {
        'is_required': u'Debe introducir al menos un permiso',
        'is_invalid': u'Permiso incorrecto',
    }

    def validate(self, value):


        perm_list = list(value)

        if (len(perm_list) == 0):
            raise ValidationError(self.error_messages['is_required'])

        x = 0

        new_values = []
        for perm in perm_list:
            if perm == '':
                continue
            if len(Permission.objects.filter(codename=perm)) == 0:
                raise ValidationError(self.error_messages['is_invalid'])

            new_values.append(perm)
            x = x + 1

        if (x == 0):
            raise ValidationError(self.error_messages['is_required'])


class UserListField(StringListField):
    default_error_messages = {
        'is_invalid': u'Usuario incorrecto',
    }


    def validate(self, value):

        user_list = list(value)

        new_values = []
        for user in user_list:
            if user == '':
                continue
            if len(User.objects.filter(id=user)) == 0:
                raise ValidationError(self.error_messages['is_invalid'])

            new_values.append(user)

