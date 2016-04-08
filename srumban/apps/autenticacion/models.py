from django.db import models
from django.contrib.auth.models import User as djUser
from django.contrib.auth.models import Permission as djPermission
from django.contrib.auth.models import Group as djGroup

class User(models.Model):
    """

    This model *extends* in some way the Django default
    ``django.contrib.auth.models.User`` model, adding some fields.

    Stores information about every user from the system.

    :param id: Unique id
    :param telefono: Phone number
    :param direccion: Address

    """
    # Opcion alternativa: settings.AUTH_USER_MODEL
    user = models.OneToOneField( djUser, on_delete = models.CASCADE, verbose_name = "Usuario para Autenticacion")
    telefono = models.TextField( "Telefono" )
    direccion =  models.TextField( "Direccion" )

    def __str__(self):
        dataString = "<{u.username}, first name: {u.first_name}, "\
                 "last name: {u.last_name}, email: {u.email}>"
        return dataString.format(u=self.user)

class Permission(models.Model):
    """
        This model *extends* Django default ``django.contrib.auth.models.Permission``
        model, adding one field.

        Used to manage permissions on the system.

        :param id: Unique id
        :param permission: Default model from Django. Used with the framework
        :param desc_larga: Long human readable name for a permission.

    """
    permission = models.OneToOneField( djPermission, on_delete = models.CASCADE, verbose_name = "Permiso" ) #TODO Cuidar eliminación
    desc_larga = models.TextField( "Descripcion larga" )

    def __str__(self):
        dataString = "<{p.codename}, name: {p.name}, desc_larga: {d}>"
        return dataString.format(p=self.permission, d=desc_larga)

class Group(models.Model):
    """
    This model *extends* Django default ``django.contrib.auth.models.Group``
    model, adding one field.

    Used to manage roles on the system.

    :param id: Unique id
    :param group: Default model from Django. Used with the framework
    :param desc_larga: Long human readable name for a role.

    """
    group = models.OneToOneField( djGroup, on_delete = models.CASCADE, verbose_name = "Grupo" ) #TODO Cuidar eliminación
    desc_larga = models.TextField( "Descripcion larga" )

    def __str__(self):
        dataString = "<{g.name}, desc_larga: {d}>"
        return dataString.format(g=self.group, d=self.desc_larga)
