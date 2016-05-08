from django.db import models
from django.core.exceptions import FieldError

from apps.autenticacion.models import User
from apps.administracion.models import Project

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
    project = models.ForeignKey(Project, null=False, related_name='fk_team_project')
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
        self.hs_hombre = hs
        self.save()

