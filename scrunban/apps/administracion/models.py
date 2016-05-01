from django.db import models
from apps.autenticacion.models import User

# Create your models here.


class ProductBacklog(models.Model):
    id = models.AutoField(primary_key=True)
    def __str__(self):
        return "%d" % self.id

class SprintBacklog(models.Model):
    id = models.AutoField(primary_key=True)
    def __str__(self):
        return "%d" % self.id

class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=128)
    fechaInicio = models.DateField()
    fechaFinal = models.DateField()
    scrumMaster = models.ForeignKey(User, null=True, related_name='asdf')
    productOwner = models.ForeignKey(User, null=True, related_name='asdf2')
    developmentTeam = models.ManyToManyField(User, related_name='asdf3')
    productBacklog = models.OneToOneField(ProductBacklog)
    sprintBacklog = models.ForeignKey(SprintBacklog, null=True)
    def __str__(self):
        return "%s" % self.nombre

class Sprint(models.Model):
    id = models.AutoField(primary_key=True)
    sprint = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    def __str__(self):
        return "%d" % self.id

