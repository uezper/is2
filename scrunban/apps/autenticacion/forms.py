from django import forms
from apps.autenticacion.settings import DEF_ROLE_SCRUM_MASTER
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from apps.autenticacion.models import User, Project

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



class CreateRolForm(forms.Form):

    projectID = forms.CharField(widget=forms.HiddenInput)
    inputNombre = forms.CharField(min_length=1, required=True,widget=forms.HiddenInput, error_messages={'required' : 'Debe introducir el nombre del Rol'})
    inputPerms = PermissionListField(widget=forms.HiddenInput)
    inputUsers = UserListField(widget=forms.HiddenInput)

    def clean_inputPerms(self):
        perms = self.cleaned_data['inputPerms']
        new_perms = []

        for perm in perms:
            if perm != '':
                new_perms.append(Permission.objects.filter(codename=perm)[0])

        return new_perms

    def clean_inputUsers(self):
        users = self.cleaned_data['inputUsers']
        new_users = []

        for user in users:
            if user != '':
                new_users.append(User.objects.filter(id=user)[0])


        return new_users

    def clean_inputNombre(self):

        project = Project.objects.filter(id=self.cleaned_data['projectID'])[0]
        name = self.cleaned_data['inputNombre']

        for rol in project.get_roles():
            if rol.get_desc() == name:
                raise ValidationError('Ya existe un rol con ese nombre')

        return self.cleaned_data['inputNombre']

class DeleteRolForm(forms.Form):

    error_messages = {
        'required': 'Debe introducir el nombre del Rol',
        'not_exist' : 'El rol especificado no existe',
    }

    inputID = forms.CharField(required=True,widget=forms.HiddenInput, error_messages=error_messages)

    def clean_inputID(self):
        from apps.autenticacion.models import Role
        rol = Role.objects.filter(id=self.cleaned_data['inputID'])
        if (len(rol) == 0):
            raise ValidationError(self.error_messages['not_exist'])

        return rol[0]



class EditRolForm(CreateRolForm):

    inputOldNombre = forms.CharField(min_length=1, required=True, widget=forms.HiddenInput)
    projectID = forms.CharField(widget=forms.HiddenInput)
    inputNombre = forms.CharField(min_length=1, required=True, widget=forms.HiddenInput,                                  error_messages={'required': 'Debe introducir el nombre del Rol'})
    inputPerms = PermissionListField(widget=forms.HiddenInput)
    inputUsers = UserListField(widget=forms.HiddenInput)

    def clean_inputNombre(self):

        if (self.cleaned_data['inputNombre'] == self.data['inputOldNombre']):
            return self.cleaned_data['inputNombre']

        project = Project.objects.filter(id=self.cleaned_data['projectID'])[0]
        name = self.cleaned_data['inputNombre']

        for rol in project.get_roles():
            if rol.get_desc() == name:
                raise ValidationError('Ya existe un rol con ese nombre')

        return self.cleaned_data['inputNombre']

    def clean_inputUsers(self):

        users = self.cleaned_data['inputUsers']
        new_users = []

        for user in users:
            if user != '':
                new_users.append(User.objects.filter(id=user)[0])

        from apps.autenticacion.settings import DEF_ROLE_SCRUM_MASTER

        project = Project.objects.filter(id=self.cleaned_data['projectID'])[0]
        rol_name = ''
        for rol in project.get_roles():
            if rol.get_desc() == self.cleaned_data['inputNombre']:
                rol_name = rol.get_name()

        if (self.cleaned_data['projectID'] + '_' + DEF_ROLE_SCRUM_MASTER[0] == rol_name):
            if (len(new_users) == 0):
                raise ValidationError('Este rol debe tener como minimo un usuario')

        return new_users