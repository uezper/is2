from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from apps.autenticacion.models import User
from apps.administracion.models import Project
from apps.proyecto.fields import PermissionListField, UserListField


class CreateRolForm(forms.Form):
    """
    Formulario que se encarga de validar los datos necesarios para la creacion de un nuevo rol

    :param projectID: ID del proyecto
    :param inputNombre: Nombre del rol (descripcion larga)
    :param inputPerms: Lista de permisos (codename de los permisos)
    :param inputUsers: Lista de usuarios (sus id) * Este campo es opcional
    """

    projectID = forms.CharField(widget=forms.HiddenInput,required=True)
    inputNombre = forms.CharField(min_length=1, required=True,widget=forms.HiddenInput, error_messages={'required' : 'Debe introducir el nombre del Rol'})
    inputPerms = PermissionListField(widget=forms.HiddenInput)
    inputUsers = UserListField(widget=forms.HiddenInput)

    def clean_projectID(self):
        project_id = self.cleaned_data.get('projectID','')
        project = Project.objects.filter(id=project_id)

        if (len(project) == 0):
            raise ValidationError('El proyecto no existe')
        else:
            return self.cleaned_data.get('projectID','')

    def clean_inputPerms(self):
        perms = self.cleaned_data.get('inputPerms',[])
        new_perms = []

        for perm in perms:
            if perm != '':
                new_perms.append(Permission.objects.filter(codename=perm)[0])

        return new_perms

    def clean_inputUsers(self):
        users = self.cleaned_data.get('inputUsers',[])
        new_users = []

        for user in users:
            if user != '':
                new_users.append(User.objects.filter(id=user)[0])


        return new_users

    def clean_inputNombre(self):

        project_id = self.cleaned_data.get('projectID', '')

        if (project_id == ''):
            return ''

        project = Project.objects.filter(id=project_id)[0]
        name = self.cleaned_data['inputNombre']

        for rol in project.get_roles():
            if rol.get_desc() == name:
                raise ValidationError('Ya existe un rol con ese nombre')

        return self.cleaned_data.get('inputNombre','')

    def save(self):
        if self.is_valid():
            perms = self.cleaned_data['inputPerms']
            users = self.cleaned_data['inputUsers']
            rol_name = self.cleaned_data['inputNombre']
            project = Project.objects.filter(id=self.cleaned_data['projectID'])[0]

            rol = project.add_rol(desc_larga=rol_name)

            for p in perms:
                rol.add_perm(p)

            for u in users:
                rol.add_user(u)


class EditRolForm(CreateRolForm):
    """
        Formulario que se encarga de validar los datos necesarios para la edicion de un rol

        :param projectID: ID del proyecto
        :param inputNombre: Nombre nuevo del rol (descripcion larga)
        :param inputOldNombre: Nombre actual del rol (descripcion larga)
        :param inputPerms: Lista de permisos (codename de los permisos)
        :param inputUsers: Lista de usuarios (sus id) * Este campo es opcional

    """
    inputOldNombre = forms.CharField(min_length=1, required=True, widget=forms.HiddenInput)
    projectID = forms.CharField(widget=forms.HiddenInput)
    inputNombre = forms.CharField(min_length=1, required=True, widget=forms.HiddenInput,                                  error_messages={'required': 'Debe introducir el nombre del Rol'})


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
            if rol.get_desc() == self.data['inputOldNombre']:
                rol_name = rol.get_name()

        if (self.cleaned_data['projectID'] + '_' + DEF_ROLE_SCRUM_MASTER[0] == rol_name):
            if (len(new_users) == 0):
                raise ValidationError('Este rol debe tener como minimo un usuario')

        return new_users

    def save(self):
        if self.is_valid():
            perms = self.cleaned_data['inputPerms']
            users = self.cleaned_data['inputUsers']
            project = Project.objects.filter(id=self.cleaned_data['projectID'])[0]

            rol = None
            for r in project.get_roles():
                if r.get_desc() == self.cleaned_data['inputOldNombre']:
                    rol = r

            rol.set_desc(self.cleaned_data['inputNombre'])

            for p in rol.group.permissions.all():
                rol.remove_perm(p)

            for u in rol.group.user_set.all():
                rol.remove_user(u.user)

            for p in perms:
                rol.add_perm(p)

            for u in users:
                rol.add_user(u)


class DeleteRolForm(EditRolForm):
    """
        Formulario que se encarga de validar los datos necesarios para eliminar un rol

        :param projectID: ID del proyecto
        :param inputID: ID del rol que se va a borrar

    """

    error_messages = {
        'required': 'Debe introducir el nombre del Rol',
        'not_exist' : 'El rol especificado no existe',
        'not_allowed': 'No esta permitido borrar este rol'
    }

    inputID = forms.CharField(required=True,widget=forms.HiddenInput, error_messages=error_messages)

    def clean_inputID(self):
        from apps.autenticacion.models import Role
        rol = Role.objects.filter(id=self.cleaned_data['inputID'])
        if (len(rol) == 0):
            raise ValidationError(self.error_messages['not_exist'])

        from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES
        for r in DEFAULT_PROJECT_ROLES:
            if (rol[0].get_name().endswith(r[0])):
                raise ValidationError(self.error_messages['not_allowed'])

        return rol[0]

    def save(self):
        if self.is_valid():
            rol = self.cleaned_data['inputID']
            project_id = self.cleaned_data['projectID']
            project = Project.objects.filter(id=project_id)[0]

            project.remove_rol(short_name=rol.get_name())
