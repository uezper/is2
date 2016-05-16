from django.db import models
from django.dispatch import receiver
from apps.autenticacion.models import User, Role
from apps.proyecto.models import Sprint, Project, Team
from django.utils import timezone

class UserStory(models.Model):
    """
    Modelo donde se almacena la información sobre cada actividad a realizar dentro del projecto.
    """
    # Public fields mapped to DB columns
    description = models.CharField('Descripcion', max_length=140) # Twetter..?? XD
    details = models.TextField('Detalles')
    acceptance_requirements = models.TextField('Requisitos de Aceptacion')
    estimated_time = models.IntegerField('Tiempo estimado') # tiempo para su finalizacion en horas
    business_value = models.FloatField('Valor de negocio')
    tecnical_value = models.FloatField('Valor tecnico')
    urgency = models.FloatField('Urgencia')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    allowed_developers = models.ManyToManyField(User)

    # Public fields for simplicity
    user_stories = models.Manager() # Alias
    objects = models.Manager()

    def get_notes(self):
        return Note.notes.filter(user_story=self)

    def get_weight(self):
        return (self.business_value + self.urgency + 2 * self.tecnical_value)/4
    
    def __str__(self):
        return "{}".format(self.description)

# TODO Add unit tests and extend model!
class Grained(models.Model):
    # Public fields mapped to DB columns
    user_story = models.ForeignKey(UserStory)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    # TODO activity = ...
    # TODO state = ...
    developers = models.ManyToManyField(Team)

    # Public fields for simplicity
    graineds = models.Manager() # Alias
    objects = models.Manager()
    
class Note(models.Model):
    """
    Modelo para almacenar notas sobre un User Story
    """
    # Public fields mapped to DB columns
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField()
    grained = models.ForeignKey(Grained, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work_load = models.PositiveIntegerField(default=0)
    aproved = models.BooleanField(default=False)
    aproved_note = models.TextField(default='[Unaproved]')

    # Public fields for simplicity
    notes = models.Manager() # Alias
    objects = models.Manager()

class Flow(models.Model):
    # Public fields mapped to DB columns
    name = models.TextField()
    project = models.ForeignKey(Project)
    
    # Public fields for simplicity
    flows = models.Manager() # Alias
    objects = models.Manager()

    def __str__(self):
        return "{} of {}".format(self.name, self.project)

class UserStoryType(models.Model):
    """
    Modelo que determina a cuales Flujos puede pertenecer un User Story.

    :param name: Nombre del Tipo de User Story
    """
    # Public fields mapped to DB columns
    name = models.TextField()
    flows = models.ManyToManyField(Flow)

    # Public fields for simplicity
    types = models.Manager() # Alias
    objects = models.Manager()

    def __str__(self):
        return "{}".format(self.name)
