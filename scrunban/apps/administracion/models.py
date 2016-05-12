from django.db import models
from django.dispatch import receiver
from apps.autenticacion.models import User, Role
from apps.proyecto.models import Sprint, Project, Team

class UserStory(models.Model):
    """
    Modelo donde se almacena la información sobre cada actividad a realizar dentro del projecto.
    """
    # Public fields mapped to DB columns
    description = models.CharField(max_length=140) # Twetter..?? XD
    details = models.TextField()
    acceptance_requirements = models.TextField()
    estimated_time = models.IntegerField() # tiempo para su finalizacion en horas
    business_value = models.FloatField()
    tecnical_value = models.FloatField()
    urgency = models.FloatField()
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
    
class Note(models.Model):
    """
    Modelo para almacenar notas sobre un User Story
    """
    # Public fields mapped to DB columns
    note = models.TextField()
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Public fields for simplicity
    notes = models.Manager() # Alias
    objects = models.Manager()

# TODO Add unit tests and extend model!
class Grained(models.Model):
    # Public fields mapped to DB columns
    user_story = models.ForeignKey(UserStory)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    developers = models.ManyToManyField(Team)

    # Public fields for simplicity
    objects = models.Manager()

