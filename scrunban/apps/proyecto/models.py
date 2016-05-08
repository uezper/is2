from django.db import models
from django.core.exceptions import FieldError

from apps.autenticacion.models import User
from apps.administracion.models import Project, SprintBacklog

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

        sec = 0
        if not(sprints.count() == 0):
            sec = sprints.last().sec

        sb = SprintBacklog()
        sb.save()

        sprint_ = Sprint()
        sprint_.sec = sec + 1
        sprint_.project = kwargs['project']
        sprint_.estimated_time = kwargs['estimated_time']
        sprint_.state = sprint_.state_choices[0][0]
        sprint_.sprint_backlog = sb
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
    :param sprint_backlog: Sprint Backlog

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
    sprint_backlog = models.ForeignKey(to=SprintBacklog, null=True, blank=True)

    objects = models.Manager()
    sprints = SprintManager()


    def __str__(self):
        return "Sprint %d" % self.id

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
        if state in self.state_choices:
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

    def get_sprint_backlog(self):
        """
        Retorna el Sprint Backlog
        :returns: Sprint Backlog
        """
        return self.sprint_backlog
