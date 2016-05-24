from django.db import models
from django.dispatch import receiver
from apps.autenticacion.models import User, Role
from apps.proyecto.models import Sprint, Project, Team, Flow, Activity
from django.utils import timezone

class UserStoryType(models.Model):
    """
    Modelo que determina a cuales Flujos puede pertenecer un User Story.

    :param name: Nombre del Tipo de User Story
    """
    # Public fields mapped to DB columns
    project = models.ForeignKey(Project)
    name = models.TextField()
    flows = models.ManyToManyField(Flow)

    # Public fields for simplicity
    types = models.Manager() # Alias
    objects = models.Manager()

    def __str__(self):
        return "{}".format(self.name)

class UserStory(models.Model):
    """
    Modelo donde se almacena la información sobre cada actividad a realizar dentro del projecto.
    """
    # Public fields mapped to DB columns

    states = ['Pendiente', 'Ejecutando', 'Finalizado']

    description = models.CharField(max_length=140)
    details = models.TextField()
    acceptance_requirements = models.TextField()
    estimated_time = models.IntegerField() # tiempo para su finalizacion en horas
    business_value = models.FloatField()
    tecnical_value = models.FloatField()
    urgency = models.FloatField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    us_type = models.ForeignKey(UserStoryType, on_delete=models.SET_NULL, null=True)
    state = models.IntegerField(default=0)
    delay_urgency = models.IntegerField(default=0)

    # Public fields for simplicity
    user_stories = models.Manager() # Alias
    objects = models.Manager()

    def get_notes(self):
        return Note.notes.filter(user_story=self)

    def get_weight(self):
        return (self.business_value + self.urgency + 2 * self.tecnical_value)/4 + self.delay_urgency
    
    def __str__(self):
        return "{}".format(self.description)

# TODO Add unit tests and extend model!
class Grained(models.Model):
    # Public fields mapped to DB columns
    user_story = models.ForeignKey(UserStory)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True)
    state = models.IntegerField(default=1)
    developers = models.ManyToManyField(Team)
    flow = models.ForeignKey(Flow, default=None, null=True, on_delete=models.SET_NULL)

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


