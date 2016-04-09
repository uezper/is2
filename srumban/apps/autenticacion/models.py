from django.db import models
from django.contrib.auth.models import User as djUser
from django.contrib.auth.models import Permission as djPermission
from django.contrib.auth.models import Group as djGroup

class User(models.Model):
    """

    Este modelo *extiende* (no hereda) el model por defecto de Django:
    ``django.contrib.auth.models.User``, agregando algunos campos.

    El model se encarga de guardar informacion de todos los usuarios del sistema

    :param id: Id unico
    :param user: Model por defecto de Django. Usado con la funcion de autenticacion del framework.
    :param telefono: Nro. de Telefono
    :param direccion: Direccion

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
        Este modelo *extiende* (no hereda) el model por defecto de Django:
        ``django.contrib.auth.models.Permission``, agregando un campo.

        El model es usado para manejar los permisos en el sistema.

        :param id: Id unico
        :param permission: Modelo por defecto de Django. Usado con el framework
        :param desc_larga: Descripcion larga de un permiso (nombre legible para usuario)

    """
    permission = models.OneToOneField( djPermission, on_delete = models.CASCADE, verbose_name = "Permiso" ) #TODO Cuidar eliminación
    desc_larga = models.TextField( "Descripcion larga" )

    def __str__(self):
        dataString = "<{p.codename}, name: {p.name}, desc_larga: {d}>"
        return dataString.format(p=self.permission, d=desc_larga)

class Group(models.Model):
    """
    Este modelo *extiende* (no hereda) el model por defecto de Django:
    ``django.contrib.auth.models.Group``, agregando un campo.

    El model es usado para manejar los roles en el sistema.

    :param id: Id unico
    :param group: Modelo por defecto de Django. Usado con el framework
    :param desc_larga: Descripcion larga de un rol (nombre legible para usuario)

    """
    group = models.OneToOneField( djGroup, on_delete = models.CASCADE, verbose_name = "Grupo" ) #TODO Cuidar eliminación
    desc_larga = models.TextField( "Descripcion larga" )

    def __str__(self):
        dataString = "<{g.name}, desc_larga: {d}>"
        return dataString.format(g=self.group, d=self.desc_larga)
