import uuid
from django.db import models

# Create your models here.

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=128)
    def __str__(self):
        return "%s" % self.nombre

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
    scrumMaster = models.ForeignKey(Usuario, null=True, related_name='asdf')
    developmentTeam = models.ManyToManyField(Usuario, related_name='asdff')
    productOwner = models.ForeignKey(Usuario, null=True, related_name='asdfa')
    productBacklog = models.OneToOneField(ProductBacklog)
    sprintBacklog = models.ForeignKey(SprintBacklog, null=True)
    def __str__(self):
        return "%s" % self.nombre

class Sprint(models.Model):
    id = models.AutoField(primary_key=True)
    sprint = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    def __str__(self):
        return "%d" % self.id

