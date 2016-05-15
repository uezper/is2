from django.db import models
from django.dispatch import receiver
from django.core.exceptions import FieldError

from apps.autenticacion.models import User, Role

class ProjectManager(models.Manager):
    def create(self, **kwargs):
        """
        Wrapper of the creation function for Project.
        :param kwargs: Project data.
        :returns: None if the project has not been created or
        the instance of the new project.
        """
        # Checking for required fields

        required_fields = ['name', 'date_start', 'date_end', 'scrum_master', 'product_owner']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        # Checking if name has already been taken

        if Project.projects.filter(name=kwargs['name']).count() == 0:
            data = {}
            for f in required_fields:
                data[f] = kwargs[f]

            p = Project()
            
            p.name = data['name']
            p.date_start = data['date_start']
            p.date_end = data['date_end']
            p.scrum_master = data['scrum_master']
            p.product_owner = data['product_owner']

            p.save()

            # Crea roles por defecto
            from apps.autenticacion.settings import DEFAULT_PROJECT_ROLES
            from django.contrib.auth.models import Permission

            for rol in DEFAULT_PROJECT_ROLES:
                role_data = {
                    'name': rol[0],
                    'desc_larga': rol[1]
                }

                new_rol = p.add_rol(**role_data)
                for perm_ in rol[2]:
                    perm = Permission.objects.get(codename=perm_[0])
                    new_rol.add_perm(perm)

            p_id = p.id
            for rol in p.get_roles():
                if rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[0][0]:
                    rol.add_user(data['scrum_master'])
                elif rol.get_name() == str(p_id) + '_' + DEFAULT_PROJECT_ROLES[1][0]:
                    rol.add_user(data['product_owner'])



            return p
        else:
            return None

    def filter(self, **kwargs):
        """
        Returns the results of a query.
        :param kwargs: Query details.
        :returns: An instance of QuerySet containing the results of the query.
        """
        return Project.objects.filter(**kwargs)


class Project(models.Model):
    """

    El model se encarga de guardar informacion de todos los proyectos del sistema.

    :param id: Id unico
    :param name: Nombre del proyecto
    :param date_start: Fecha de inicio del proyecto
    :param date_end: Fecha de finalizacion del proyecto
    :param scrum_master: Scrum Master del proyecto
    :param product_owner: Product Owner del proyecto
    :param development_team: Todos los Development Teams del proyecto
    :param capacity: Capacidad del Equipo de desarrollo del proyecto
    """
    # Public fields mapped to DB columns
    id = models.AutoField(primary_key=True)
    name = models.TextField('Project name', unique=True)
    date_start = models.DateField()
    date_end = models.DateField()
    scrum_master = models.ForeignKey(User, null=True, related_name='fk_project_scrum_master')
    product_owner = models.ForeignKey(User, null=True, related_name='fk_project_product_owner')
    development_team = models.ManyToManyField(User, related_name='mm_project_development_team')
    capacity = models.IntegerField(default=0)

    # Public fields for simplicity
    objects = models.Manager()
    projects = ProjectManager()

    def __str__(self):
        return "{}".format(self.name)


    def get_name(self):
        """
        Returns the project name
        """
        return self.name

    def add_rol(self, **kwargs):
        """

        Crea un rol de proyecto con un nombre de la forma ``idProyecto_name`` si es que ``name`` es especificado,
         de lo contrario el nombre queda de la forma ``idProyecto_r_num`` donde ``num`` va aumentando secuencialmente.


        :param desc_larga:  Descripcion larga del Rol
        :param name:  Nombre en codigo del Rol
        :returns: Instancia del nuevo rol creado
        """

        required_fields = ['desc_larga']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        p_id = self.id
        r_name = ''

        if ('name' not in kwargs.keys()):
            r_tot = Role.objects.filter(group__name__startswith=str(p_id) + '_r_')
            if (len(r_tot) == 0):
                r_name = str(p_id) + '_r_0'
            else:
                r_last = r_tot.last().get_name()
                r_last = int(r_last[len(r_last) - 1]) + 1
                r_name = str(p_id) + '_r_' + str(r_last)
        else:
            r_name = str(p_id) + '_' + kwargs['name']

        data = {
            'name': r_name,
            'desc_larga': kwargs['desc_larga'],

        }
        new_rol = Role.roles.create(**data)
        return new_rol

    def remove_rol(self, short_name):
        """

        Remueve un rol de un proyecto

        :param short_name: Nombre en codigo del Rol
        """

        p_id = self.id
        Role.objects.filter(group__name=short_name)[0].delete()

    def get_roles(self):

        """

        Obtiene una lista de todos los roles asociados con el proyecto

        :returns: Una lista de roles
        """

        p_id = self.id
        roles = Role.objects.filter(group__name__startswith=str(p_id) + '_')

        return roles


    def get_user_perms(self, user):
        """

        Obtiene una lista de todos los permisos de un Usuario asociados al proyecto a traves de algun rol

        :param user: Instancia de usuario (autenticacion.models.User)
        :returns: Lista de permisos
        """
        p_id = self.id
        roles = user.user.groups.filter(name__startswith=str(p_id) + '_')

        perms = []

        for rol in roles:
            perms += rol.permissions.all()

        return perms

    def has_perm(self, user, perm):
        """

        Verifica si un usuario tiene un permiso dado dentro de un proyecto

        :param user: Instancia de usuario que se va a verificar que tenga el permiso (autenticacion.models.User)
        :param perm: Permiso que se desea verificar en su nombre en codigo
        :return:
        """

        for p in self.get_user_perms(user):
            if (p.codename == perm):
                return True

        return False


@receiver(models.signals.post_delete, sender=Project, dispatch_uid='project_delete_signal')
def project_delete(sender, instance, *args, **kwargs):
    """
    Escucha al evento de eliminación de Project para eliminar los roles asociados
    """
    for rol in instance.get_roles():
        rol.delete()

class TeamManager(models.Manager):
    """
    Clase administradora de operaciones a nivel de tabla del modelo ``Team``.
    """

    def create(self, **kwargs):
        """
        Crea una asociacion entre usuario y proyecto con cantidad de hs-hombre.
        :param kwargs: Usuario, proyecto y cantidad de hs-hombre.
        :returns: En caso de haberse creado, una instancia. Sino ``None``
        """

        # Checking for required fields
        required_fields = ['user', 'project', 'hs']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        # Checking if relation already exists
        if Team.objects.filter(user=kwargs['user'], project=kwargs['project']).count() == 0:
            team_ = Team()
            team_.user = kwargs['user']
            team_.project = kwargs['project']
            team_.hs_hombre = kwargs['hs']
            team_.save()
            return team_
        else:
            return None

    def filter(self, **kwargs):
        """
        Returns the results of a query.
        :param kwargs: Query details.
        :returns: An instance of QuerySet containing the results of the query.
        """

        custom_user_fields = ['user', 'project']

        # Check arguments
        accepted_fields = custom_user_fields
        for key in kwargs.keys():
            if key not in accepted_fields:
                raise FieldError('Cannot resolve {} into field.'.format(key))

        # Construct params
        params = {}
        for key, value in kwargs.items():
                params[key] = value

        # Make query and return
        return Team.objects.filter(**params)

class Team(models.Model):
    """
    Este modelo se encarga de manejar la cantidad de Hs-Hombre asignadas a cada usuario
    perteneciente al equipo de desarrollo de un proyecto.

    :param id: Id unico
    :param user: Instancia de usuario (``apps.autenticacion.models.User``)
    :param project: Instancia de proyecto (``apps.administracion.models.Project``)
    :param hs_hombre: Capacidad hs-hombre del usuario dentro del proyecto

    """
    user = models.ForeignKey(User, null=False, related_name='fk_team_user')
    project = models.ForeignKey(to=Project, null=False, related_name='fk_team_project',on_delete=models.CASCADE)
    hs_hombre = models.IntegerField("Hs Hombre")

    objects = models.Manager()
    teams = TeamManager()


    def get_hsHombre(self):
        """
        Retorna la cantidad de hs-hombre del Usuario dentro del proyecto

        :return: Cantidad de hs-Hombre del Usuario dentro del proyecto
        """
        return self.hs_hombre

    def set_hsHombre(self, hs):
        """
        Cambia la cantidad de hs-hombre de un Usuario dentro del proyecto

        :param hs: Cantidad de hs-hombre
        """

        self.project.capacity -= self.hs_hombre
        self.project.capacity += hs
        self.project.save()
        self.hs_hombre = hs
        self.save()



class SprintManager(models.Manager):
    """
    Clase administradora de operaciones a nivel de tabla del modelo ``Team``.
    """

    def create(self, **kwargs):
        """
        Crea un Sprint dentro de un proyecto.
        :param kwargs: Proyecto, Tiempo estimado y Capacidad
        :returns: En caso de haberse creado, una instancia. Sino ``None``
        """

        # Checking for required fields
        required_fields = ['project', 'estimated_time']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))



        sprints = Sprint.objects.filter(project=kwargs['project'])

        sec = 1
        if not(sprints.count() == 0):
            sec = sprints.last().sec


        sprint_ = Sprint()
        sprint_.sec = sec + 1
        sprint_.project = kwargs['project']
        sprint_.estimated_time = kwargs['estimated_time']
        sprint_.state = sprint_.state_choices[0][0]
        sprint_.real_time = 0
        sprint_.save()

        return sprint_

    def filter(self, **kwargs):
        """
        Returns the results of a query.
        :param kwargs: Query details.
        :returns: An instance of QuerySet containing the results of the query.
        """

        custom_user_fields = ['project', 'state']

        # Check arguments
        accepted_fields = custom_user_fields
        for key in kwargs.keys():
            if key not in accepted_fields:
                raise FieldError('Cannot resolve {} into field.'.format(key))

        # Construct params
        params = {}
        for key, value in kwargs.items():
                params[key] = value

        # Make query and return
        return Sprint.objects.filter(**params)


class Sprint(models.Model):
    """
    Modelo encargado de manejar los Sprints de un proyecto

    :param id: Id unico
    :param sec: Entero positivo secuencial dentro del proyecto
    :param project: Instancia de Proyecto
    :param state: Estado del Sprint. Puede ser uno de los siguientes: 'Pendiente', 'Ejecuciom', 'Finalizado' o 'Cancelado'
    :param estimated_time: Tiempo estimado para la finalizacion del Sprint, en dias
    :param real_time: Duracion real del Sprint
    :start_date: Fecha de inicio de ejecucion del Sprint

    """
    state_choices = (
        ('Pendiente','Pendiente'),
        ('Ejecucion','En ejecucion'),
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado')

    )

    id = models.AutoField(primary_key=True)
    sec = models.IntegerField(null=False)
    project = models.ForeignKey(to=Project, null=True, blank=True, on_delete=models.CASCADE)
    state = models.CharField(max_length=15, choices=state_choices, default=state_choices[0][0], null=False)
    estimated_time = models.IntegerField(null=False) # en dias
    real_time = models.IntegerField(null=False) # en dias
    start_date = models.DateField(null=True)

    objects = models.Manager()
    sprints = SprintManager()


    def __str__(self):
        return "Sprint %d" % self.sec

    def get_name(self):
        """
        Retorna el nombre del Sprint
        :returns: Nombre del Sprint
        """
        return "Sprint %d" % self.id

    def get_project(self):
        """
        Retorna el proyecto al cual pertenece el Sprint
        :returns: Istancia de proyecto
        """
        return self.project

    def get_state(self):
        """
        Retorna el Estado actual del Sprint
        :returns: Estado del Sprint
        """
        return self.state

    def set_state(self, state):
        """
        Modifica el estado del Sprint
        :param state: Nuevo estado. Puede ser uno de los siguientes: 'Pendiente', 'Ejecuciom', 'Finalizado' o 'Cancelado'
        """
        if state in [st[0] for st in self.state_choices]:
            self.state = state
            self.save()

    def get_estimated_time(self):
        """
        Retorna el tiempo estimado para la finalizacion del Sprint en dias
        :returns: Tiempo estimado de finalizacion
        """
        return self.estimated_time

    def set_estimated_time(self, time):
        """
        Modifica el tiempo de duracion estimada
        :param time: Duracion estimada
        """
        self.estimated_time = time
        self.save()

    def get_real_time(self):
        """
        Retorna el tiempo de duracion real del Sprint
        :returns: Tiempo de duracion real
        """
        return self.get_real_time


    def get_start_date(self):
        """
        Retorna la hecha en la cual inicio la ejecucion del Sprint
        :returns: Fecha de inicio de ejecucion
        """
        return self.start_date

    def set_start_date(self, fecha):
        """
        Modifica la fecha de inicio de ejecucion del Sprint
        :param fecha: Fecha de inicio de ejecucion
        """
        self.start_date = fecha
        self.save()

