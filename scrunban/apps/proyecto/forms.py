import logging
from scrunban.settings import base as base_settings

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission

from apps.autenticacion.models import User
from apps.administracion.models import Project
from apps.proyecto.fields import PermissionListField, UserListField, SprintBacklogField, ActivitiesField


# Define loggers
stdlogger = logging.getLogger(base_settings.LOGGERS_NAME['proyecto'])

# Define log entries formatters
def formatter(entity, project, action, actor):
    return '{} de {} ha sido {} por {}'.format(entity, project, action, actor)


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
            rol.save()

            from apps.autenticacion.models import Role
            from django.contrib.auth.models import Permission
            from apps.autenticacion.settings import PROJECT_US_DEVELOP
            from apps.proyecto.models import Team

            old_perms = rol.get_perms()
            p_ = Permission.objects.get(codename=PROJECT_US_DEVELOP[0])
            save_hs = False
            if p_ in old_perms:
                save_hs = True
                for u in users:
                    team_ = Team.objects.filter(user=u,project=project)
                    if len(team_) != 0:
                        u.temp_ = team_[0].hs_hombre

            for u in rol.group.user_set.all():
                rol.remove_user(u.user)

            for p in rol.group.permissions.all():
                rol.remove_perm(p)

            for p in perms:
                rol.add_perm(p)

            for u in users:
                rol.add_user(u)
                if (save_hs):
                    x = Team.objects.filter(user=u,project=project)[0]
                    if hasattr(u, 'temp_'):
                        x.hs_hombre = u.temp_
                    else:
                        x.hs_homre = 1
                    x.save()

                


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

            from datetime import date, timedelta

            project_date_end = Project.objects.get(id=self.data['project']).date_end

            if project_date_end != None:
                today = date.today()
                sprint_end = today + timedelta(days=self.cleaned_data['estimated_time'])

                if (project_date_end - sprint_end).days < 0:
                    raise ValidationError('El Sprint finalizaria pasada la fecha de finalizacion del proyecto: {}/{}/{}'.format(project_date_end.day, project_date_end.month, project_date_end.year))

            return self.cleaned_data['estimated_time']
        else:
            raise ValidationError('Este campo debe ser un entero positivo mayor que cero')

    def clean_sprint_backlog(self):

        from apps.administracion.models import UserStory, Grained
        from apps.proyecto.models import Team, Flow, Activity


        new_sb = []
        devs = []

        for reg in self.cleaned_data['sprint_backlog']:
            us = reg.split(':')

            if len(us) != 4:
                raise ValidationError('Error en el SprintBacklog. Introduzca todos los datos e intente de nuevo');

            us_id = us[0]
            us_devs = us[1].split('_')
            us_flujo = Flow.objects.filter(id=us[2])
            us_actividad = Activity.objects.filter(id=us[3])


            us_ = UserStory.objects.filter(id=us_id)
            if len(us_) == 0:
                raise ValidationError('Ha ingresado un US invalido: ' + us_id)
            else:
                us_ = us_[0]

                if (UserStory.states[us_.state] == 'Finalizado'):
                    raise ValidationError('El us no puede estar aqui: ' + us_.description)

                for g in Grained.objects.filter(user_story=us_):
                    if not(g.sprint.state in ['Finalizado', 'Cancelado']):
                        raise ValidationError('El us no puede estar aqui: ' + us_.description)


                if len(us_devs) == 0:
                    raise ValidationError('No ha ingresado desarrolladores para ' + us_.description)
                elif len(us_flujo) == 0:
                    raise ValidationError('Ha ingresado un flujo invalido para ' + us_.description)
                elif len(us_actividad) == 0:
                    raise ValidationError('Ha ingresado una actividad invalida para ' + us_.description)
                else:

                    us_flujo = us_flujo[0]
                    us_actividad = us_actividad[0]

                    if not(us_flujo in us_.us_type.flows.all()):
                        raise ValidationError('Ha ingresado un flujo invalido para ' + us_.description)
                    elif us_actividad.flow != us_flujo:
                        raise ValidationError('Ha ingresado una actividad invalida para ' + us_.description)

                    new_devs = []
                    for dev in us_devs:
                        if dev == '':
                            continue

                        team_ = Team.objects.filter(id=dev)
                        if len(team_) == 0:
                            raise ValidationError('No existe el desarrollador: ' + dev)
                        else:
                            team_ = team_[0]
                            new_devs.append(team_)
                            if not(dev in devs):
                                self._capacity += team_.hs_hombre * self.cleaned_data.get('estimated_time', 0)
                                devs.append(dev)

                    self._demmand += us_.estimated_time
                    if len(new_devs) == 0:
                        raise ValidationError('No ha ingresado desarrolladores para el US ' + us_.description)
                    new_sb.append((us_, new_devs, us_flujo, us_actividad))
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
            grain.activity = us[3]
            grain.state = 1
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


    def clean_sprint_backlog(self):

        from apps.administracion.models import UserStory, Grained
        from apps.proyecto.models import Team, Flow, Activity, Sprint

        sprint_ = Sprint.objects.get(id=self.data['id'])

        new_sb = []
        devs = []

        for reg in self.cleaned_data['sprint_backlog']:
            us = reg.split(':')

            if len(us) != 4:
                raise ValidationError('Error en el SprintBacklog. Introduzca todos los datos e intente de nuevo');

            us_id = us[0]
            us_devs = us[1].split('_')
            us_flujo = Flow.objects.filter(id=us[2])
            us_actividad = Activity.objects.filter(id=us[3])

            us_ = UserStory.objects.filter(id=us_id)
            if len(us_) == 0:
                raise ValidationError('Ha ingresado un US invalido: ' + us_id)
            else:
                us_ = us_[0]

                if (UserStory.states[us_.state] == 'Finalizado'):
                    raise ValidationError('El us no puede estar aqui: ' + us_.description)

                for g in Grained.objects.filter(user_story=us_):
                    if not(g.sprint.state in ['Finalizado', 'Cancelado']) and g.sprint != sprint_:
                        raise ValidationError('El us no puede estar aqui: ' + us_.description)

                if len(us_devs) == 0:
                    raise ValidationError('No ha ingresado desarrolladores para ' + us_.description)
                elif len(us_flujo) == 0:
                    raise ValidationError('Ha ingresado un flujo invalido para ' + us_.description)
                elif len(us_actividad) == 0:
                    raise ValidationError('Ha ingresado una actividad invalida para ' + us_.description)
                else:

                    us_flujo = us_flujo[0]
                    us_actividad = us_actividad[0]

                    if not (us_flujo in us_.us_type.flows.all()):
                        raise ValidationError('Ha ingresado un flujo invalido para ' + us_.description)
                    elif us_actividad.flow != us_flujo:
                        raise ValidationError('Ha ingresado una actividad invalida para ' + us_.description)

                    new_devs = []
                    for dev in us_devs:
                        if dev == '':
                            continue

                        team_ = Team.objects.filter(id=dev)
                        if len(team_) == 0:
                            raise ValidationError('No existe el desarrollador: ' + dev)
                        else:
                            team_ = team_[0]
                            new_devs.append(team_)
                            if not (dev in devs):
                                self._capacity += team_.hs_hombre * self.cleaned_data.get('estimated_time', 0)
                                devs.append(dev)

                    self._demmand += us_.estimated_time
                    if len(new_devs) == 0:
                        raise ValidationError('No ha ingresado desarrolladores para el US ' + us_.description)
                    new_sb.append((us_, new_devs, us_flujo, us_actividad))
        return new_sb

    def save(self):
        from apps.proyecto.models import Sprint
        from apps.administracion.models import Grained

        sprint_ = Sprint.objects.get(id=self.cleaned_data['id'])
        sprint_.set_estimated_time(self.cleaned_data['estimated_time'])


        if sprint_.state == 'Pendiente':
            for grain in Grained.objects.filter(sprint=sprint_):
                grain.delete()


        for us in self.cleaned_data['sprint_backlog']:
            grain = Grained.objects.filter(sprint=sprint_, user_story=us[0])
            if len(grain) == 0:
                grain = Grained()
                grain.user_story = us[0]
                grain.sprint = sprint_
                grain.save()
            else:
                grain = grain[0]

            grain.flow = us[2]
            grain.activity = us[3]
            grain.state = 1

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

        f.save()



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


class ChangeSprintStateForm(forms.Form):
    operation = forms.CharField(required=True)

    def clean_operation(self):
        op_ = self.cleaned_data['operation']
        if op_ == '' or not(op_ in ['ejecutar', 'cancelar']):
            raise ValidationError('Operacion invalida')

        return op_


class KanbanOperation(forms.Form):
    us = forms.IntegerField(required=True, widget=forms.HiddenInput)
    grain = forms.IntegerField(required=True, widget=forms.HiddenInput)
    opt = forms.CharField(required=False, widget=forms.HiddenInput)
    operation = forms.CharField(required=True, widget=forms.HiddenInput)
    user = forms.IntegerField(required=True, widget=forms.HiddenInput)

    def clean_user(self):
        return User.objects.get(id=self.cleaned_data['user'])

    def clean_us(self):
        from apps.administracion.models import UserStory
        us = UserStory.objects.filter(id=self.cleaned_data['us'])
        if len(us) == 0:
            raise ValidationError('US invalido')
        us = us[0]
        #TODO! Comprobar estado de US, permiso de dev, grain pertenece a sprint en ejecucion

        return us

    def clean_grain(self):
        from apps.administracion.models import Grained
        return Grained.objects.get(sprint=self.cleaned_data['grain'], user_story=self.cleaned_data['us'])

    def clean_opt(self):
        if self.cleaned_data.get('opt', '') == '':
            return None
        from apps.proyecto.models import Activity

        act_ = Activity.objects.filter(id=self.cleaned_data['opt'])
        if len(act_) == 0:
            raise ValidationError('Actividad invalida')
        else:
            act_ = act_[0]
            activities_ = Activity.objects.filter(flow=self.cleaned_data['grain'].flow)

            if not (act_ in activities_):
                raise ValidationError('Actividad invalida')
            return act_

    def clean_operation(self):

        op = self.cleaned_data['operation']
        if not(op in ['move_next', 'move_prev', 'move_act', 'aprove']):
            raise ValidationError('Operacion invalida')

        from apps.proyecto.models import Activity
        from apps.administracion.models import Grained, Note

        grain = self.cleaned_data['grain']
        us_max_act = len(Activity.objects.filter(flow=grain.flow))
        opt = self.cleaned_data.get('opt', None)
        us = grain.user_story

        if op == 'move_next' and grain.state == 3 and grain.activity.sec == us_max_act:
            raise ValidationError('Operacion invalida')
        elif op == 'move_prev' and grain.state == 1 and grain.activity.sec == 1:
            raise ValidationError('Operacion invalida')
        elif op == 'move_act' and opt == None:
            raise ValidationError('Operacion invalida')
        elif op == 'aprove':
            if grain.state != 3:
                raise ValidationError('Operacion invalida')

            #TODO! Verificar permisos
            worked_time = 0
            grains_us = Grained.objects.filter(user_story=us)
            for g in grains_us:
                for note in Note.objects.filter(grained=g, aproved=True):
                    worked_time = worked_time + note.work_load
            if worked_time < us.estimated_time:
                raise ValidationError('Operacion invalida')
        return op

    def save(self):
        from apps.proyecto.models import Activity

        op = self.cleaned_data['operation']
        grain = self.cleaned_data['grain']

        activities = Activity.objects.filter(flow=grain.flow).order_by('sec')

        if (op == 'move_prev'):
            if grain.state != 1:
                grain.state = grain.state - 1
                grain.save()
            else:
                grain.activity = activities[grain.activity.sec - 2]
                grain.state = 3
                grain.save()
        elif(op == 'move_next'):
            if grain.state != 3:
                grain.state = grain.state + 1
                grain.save()
            else:
                grain.activity = activities[grain.activity.sec]
                grain.state = 1
                grain.save()
        elif(op == 'move_act'):
            grain.activity = self.cleaned_data['opt']
            grain.state = 1
            grain.save()
        elif(op == 'aprove'):
            from apps.administracion.models import Note
            from _datetime import datetime

            x = grain.user_story
            x.state = 2
            x.save()

            n = Note()
            n.grained = grain
            n.user = self.cleaned_data['user']
            n.date = datetime.utcnow()
            n.note = 'El User Story ha sido aprobado'
            n.aproved = True
            n.work_load = 0
            n.save()

            # Log event
            kwargs = {
                'entity': 'User Story {}'.format(x.description),
                'project': grain.sprint.project.name,
                'action': 'aprovado',
                'actor': self.cleaned_data['user'].user.get_full_name()
            }
            stdlogger.info(formatter(**kwargs))


class AproveNoteForm(forms.Form):
    project_id = forms.CharField(required=True, widget=forms.HiddenInput)
    user_id = forms.CharField(required=True, widget=forms.HiddenInput)
    note_id = forms.CharField(required=True, widget=forms.HiddenInput)

    def clean_project_id(self):
        return Project.objects.get(id=self.cleaned_data['project_id'])

    def clean_user_id(self):
        from apps.autenticacion.settings import PROJECT_US_APROVE

        user = User.objects.get(id=self.cleaned_data['user_id'])
        project = self.cleaned_data['project_id']

        if not(project.has_perm(user, PROJECT_US_APROVE[0])):
            raise ValidationError('Permiso denegado')

        return user

    def clean_note_id(self):
        from apps.administracion.models import Note

        note = Note.objects.filter(id=self.cleaned_data['note_id'])
        if len(note) == 0:
            raise ValidationError('Nota invalida')

        note = note[0]

        if note.aproved:
            raise ValidationError('Nota ya esta aprovada')

        if note.grained.sprint.state != 'Ejecucion':
            raise ValidationError('Operacion invalida')
        if note.grained.user_story.state != 1:
            raise ValidationError('Operacion invalida')

        return note

    def save(self):
        note = self.cleaned_data['note_id']
        note.aproved = True
        note.save()

        # Log event
        kwargs = {
            'entity': 'Nota del User Story {}'.format(note.grained.user_story.description),
            'project': note.grained.sprint.project.name,
            'action': 'aprovado',
            'actor': self.cleaned_data['user_id'].user.get_full_name()
        }
        stdlogger.info(formatter(**kwargs))



class AddWorkLoad(forms.Form):
    note = forms.CharField(required=True, widget=forms.HiddenInput)
    work_load = forms.IntegerField(required=True, widget=forms.HiddenInput)
    user = forms.IntegerField(required=True, widget=forms.HiddenInput)
    grained = forms.IntegerField(required=True, widget=forms.HiddenInput)

    def clean_note(self):
        if self.cleaned_data['note'].replace(' ', '') == '':
            raise ValidationError('La nota no puede estar vacia')
        return self.cleaned_data['note']

    def clean_workload(self):
        if self.cleaned_data['work_load'] <= 0:
            raise ValidationError('La cantidad de hs trabajadas debe ser un entero positivo mayor que cero')
        return self.cleaned_data['work_load']

    def clean_user(self):
        return User.objects.get(id=self.cleaned_data['user'])

    def clean_grained(self):
        from apps.administracion.models import Grained
        return Grained.objects.get(id=self.cleaned_data['grained'])

    def save(self):
        from apps.administracion.models import Note
        from datetime import datetime

        n = Note()
        n.work_load = self.cleaned_data['work_load']
        n.note = self.cleaned_data['note']
        n.user = self.cleaned_data['user']
        n.grained = self.cleaned_data['grained']
        n.date = datetime.utcnow()
        n.save()

        # Log event
        kwargs = {
            'entity': 'Nota del User Story {}'.format(n.grained.user_story.description),
            'project': n.grained.sprint.project.name,
            'action': 'creado',
            'actor': self.cleaned_data['user'].user.get_full_name()
        }
        stdlogger.info(formatter(**kwargs))


class DateEnd(forms.DateField):
    def validate(self, value):
        super(DateEnd, self).validate(value)
        import datetime
        now = datetime.datetime.now().date()
        if value is None:
            raise ValidationError('Este campo no puede estar vacio.')
        elif now > value:
            raise ValidationError('No se puede introducir fecha pasada.')


class StateForm(forms.Form):
    date_end = DateEnd(required=False)
