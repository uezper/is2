from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from apps.autenticacion.models import User
from apps.administracion.models import Project
from apps.proyecto.fields import PermissionListField, UserListField, SprintBacklogField, ActivitiesField


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


            for u in rol.group.user_set.all():
                rol.remove_user(u.user)

            for p in rol.group.permissions.all():
                rol.remove_perm(p)

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



class EditDevForm(forms.Form):
    """
        Formulario que se encarga de validar los datos necesarios para la edicion de la cantidad de hs-hombre de un
        miembro del equipo de desarrollo

        :param id: ID de la relacion Team
        :param username: Nombre de usuario
        :param hs_hombre: Cantidad de hs-hombre

    """
    id = forms.CharField(widget=forms.HiddenInput, required=True)
    username = forms.CharField(widget=forms.HiddenInput, required=False)
    hs_hombre = forms.IntegerField(widget=forms.HiddenInput, required=True)

    def clean_hs_hombre(self):

        if self.cleaned_data['hs_hombre'] < 0:
            raise ValidationError('La cantidad de Hs-Hombre debe ser un entero positivo')

        return self.cleaned_data['hs_hombre']

    def save(self):

        from apps.proyecto.models import Team

        team = Team.objects.get(id=self.cleaned_data['id'])
        team.set_hsHombre(self.cleaned_data['hs_hombre'])


class CreateSprintForm(forms.Form):
    """
    Formulario que se encarga de manejar la creacion de un Sprint dentro del proyecto

    :param sec: Utilizado para mostrar al usuario el nombre del Sprint
    :param estimated_time: Duracion estimada del Sprint
    :param project: Id del proyecto al cual pertenece el Sprint
    :param sprint_backlog: Lista de user stories con sus respectivos desarrolladores
    :param capacity: Capacidad del Sprint
    :param demmand: Demanda del Sprint

    """
    sec = forms.CharField(required=False, widget=forms.HiddenInput)
    estimated_time = forms.IntegerField(required=True, widget=forms.HiddenInput)
    project = forms.IntegerField(required=True, widget=forms.HiddenInput)
    sprint_backlog = SprintBacklogField(required=True, widget=forms.HiddenInput)
    capacity = forms.IntegerField(required=False, widget=forms.HiddenInput)
    demmand = forms.IntegerField(required=False, widget=forms.HiddenInput)

    _capacity = 0
    _demmand = 0

    def clean_estimated_time(self):
        if self.cleaned_data['estimated_time'] > 0:
            return self.cleaned_data['estimated_time']
        else:
            raise ValidationError('Este campo debe ser un entero positivo mayor que cero')

    def clean_sprint_backlog(self):

        from apps.administracion.models import UserStory
        from apps.proyecto.models import Team, Flow


        new_sb = []
        devs = []

        for reg in self.cleaned_data['sprint_backlog']:
            us = reg.split(':')
            us_id = us[0]
            us_devs = us[1].split('_')
            us_flujo = Flow.objects.get(id=us[2])

            us_ = UserStory.objects.filter(id=us_id)
            if len(us_) == 0:
                raise ValidationError('Ha ingresado un US invalido: ' + us_id)
            else:
                #Todo! Agregar validacion de estado y flujo cuando esten
                if len(us_devs) == 0:
                    raise ValidationError('No ha ingresado desarrolladores para el US ' + us_[0].description)
                else:
                    new_devs = []
                    for dev in us_devs:
                        if dev == '':
                            continue

                        team_ = Team.objects.filter(id=dev)
                        if len(team_) == 0:
                            raise ValidationError('No existe el desarrollador: ' + dev)
                        else:
                            new_devs.append(team_[0])
                            if not(dev in devs):
                                self._capacity += team_[0].hs_hombre * self.cleaned_data.get('estimated_time', 0)
                                devs.append(dev)

                    self._demmand += us_[0].estimated_time
                    if len(new_devs) == 0:
                        raise ValidationError('No ha ingresado desarrolladores para el US ' + us_[0].description)
                    new_sb.append((us_[0], new_devs, us_flujo))
        print(self._capacity)
        return new_sb

    def clean_capacity(self):
        return self._capacity

    def clean_demmand(self):
        self.data['capacity'] = self._capacity
        self.data['demmand'] = self._demmand

        if self._demmand > self._capacity:
            raise ValidationError('La demanda es mayor que la capacidad del Sprint')
        return self._demmand

    def clean_project(self):
        return Project.objects.get(id=self.cleaned_data['project'])

    def save(self):
        from apps.proyecto.models import Sprint
        sprint = Sprint.sprints.create(project=self.cleaned_data['project'],estimated_time=self.cleaned_data['estimated_time'])

        from apps.administracion.models import Grained

        for us in self.cleaned_data['sprint_backlog']:
            grain = Grained()
            grain.user_story = us[0]
            grain.sprint = sprint
            grain.flow = us[2]
            grain.save()
            for dev in us[1]:
                grain.developers.add(dev)
            grain.save()



class EditSprintForm(CreateSprintForm):
    """
    Formulario que se encarga de manejar la edicion de un Sprint dentro del proyecto

    :param id: Id del Sprint
    """

    id = forms.IntegerField(required=True, widget=forms.HiddenInput)

    def save(self):
        from apps.proyecto.models import Sprint
        from apps.administracion.models import Grained

        sprint_ = Sprint.objects.get(id=self.cleaned_data['id'])
        sprint_.set_estimated_time(self.cleaned_data['estimated_time'])

        for us in self.cleaned_data['sprint_backlog']:
            grain = Grained.objects.filter(sprint=sprint_, user_story=us[0])
            if len(grain) == 0:
                grain = Grained()
                grain.user_story = us[0]
                grain.sprint = sprint_
                grain.save()

            else:
                grain = grain[0]

                for dev in grain.developers.all():
                    grain.developers.remove(dev)

            for dev in us[1]:
                grain.developers.add(dev)

            grain.save()

class DeleteSprintForm(EditSprintForm):
    """
    Formulario que se encarga de manejar la eliminacion de un Sprint dentro del proyecto

    """

    def clean_demmand(self):
        return self._demmand

    def clean_sprint_backlog(self):
        return self.cleaned_data['sprint_backlog']

    def save(self):
        from apps.proyecto.models import Sprint
        sprint_ = Sprint.objects.get(id=self.cleaned_data['id'])


        sprint_.delete()

class CreateFlowForm(forms.Form):
    project = forms.IntegerField(required=True, widget=forms.HiddenInput)
    name = forms.CharField(required=True, widget=forms.HiddenInput)
    activities = ActivitiesField(required=True, widget=forms.HiddenInput)

    def clean_project(self):
        return Project.objects.get(id=self.cleaned_data['project'])

    def clean_name(self):
        from apps.proyecto.models import Flow
        f = Flow.objects.filter(project=self.cleaned_data['project'], name=self.cleaned_data['name'])
        if len(f) != 0:
            raise ValidationError('Ya existe un flujo con ese nombre dentro del proyecto')
        else:
            return self.cleaned_data['name']

    def clean_activities(self):
        from apps.proyecto.models import Activity

        ac_list = self.cleaned_data['activities']
        new_ac_list = []
        new_ac_names = []
        i = 1
        for ac in ac_list:
            if (ac in new_ac_names):
                raise ValidationError("No se puede tener actividades con nombres repetidos dentro del mismo flujo")
            new_ac = Activity()
            new_ac.name = ac
            new_ac.sec = i

            i = i + 1

            new_ac_list.append(new_ac)
            new_ac_names.append(ac)

        if len(new_ac_list) == 0:
            raise ValidationError('Debe introducir al menos una actividad')

        return new_ac_list

    def save(self):
        from apps.proyecto.models import Flow
        flow_data = {
            'name' : self.cleaned_data['name'],
            'project' : self.cleaned_data['project']
        }

        f = Flow.objects.create(**flow_data)

        for ac in self.cleaned_data['activities']:
            ac.flow = f
            ac.save()

class EditFlowForm(CreateFlowForm):
    old_name = forms.CharField(required=True, widget=forms.HiddenInput)

    def clean_name(self):
        if self.data['old_name'] == self.cleaned_data['name']:
            return self.cleaned_data['name']
        else:
            return super(EditFlowForm, self).clean_name()

    def save(self):
        from apps.proyecto.models import Flow, Activity

        f = Flow.objects.get(project=self.cleaned_data['project'], name=self.cleaned_data['old_name'])
        f.name = self.cleaned_data['name']

        for ac in Activity.objects.filter(flow=f):
            ac.delete()

        for ac in self.cleaned_data['activities']:
            ac.flow = f
            ac.save()

class DeleteFlowForm(EditFlowForm):
    project = forms.IntegerField(required=True, widget=forms.HiddenInput)
    flow = forms.IntegerField(required=True, widget=forms.HiddenInput)
    old_name = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_name(self):
        pass
    def clean_activities(self):
        pass

    def clean_project(self):
        return Project.objects.get(id=self.cleaned_data['project'])

    def clean_flow(self):
        from apps.proyecto.models import Flow
        return Flow.objects.get(id=self.cleaned_data['flow'])

    def save(self):
        f = self.cleaned_data['flow']
        f.delete()

