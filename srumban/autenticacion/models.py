from django.db import models
from django.contrib.auth.models import User as djUser
from django.contrib.auth.models import Permission as djPermission
from django.contrib.auth.models import Group as djGroup

class User(models.Model):
    """
    Modelo de usuario.

    django.contrib.auth.User ya posee los campos:
    1. username (que termina siendo el CI/RUC)
    2. password
    3. first_name
    4. last_name
    5. email
    6. groups (many-to-many)
    7. permissions (many-to-many)
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
    Modelo de Permiso.

    django.contrib.auth.Permission ya posee los campos:
    1. name (descripcion corta)
    2. content_type
    3. codename
    """
    permission = models.OneToOneField( djPermission, on_delete = models.CASCADE, verbose_name = "Permiso" ) #TODO Cuidar eliminación
    desc_larga = models.TextField( "Descripcion larga" )

    def __str__(self):
        dataString = "<{p.codename}, name: {p.name}, desc_larga: {d}>"
        return dataString.format(p=self.permission, d=desc_larga)

class Group(models.Model):
    """
    Modelo de Grupo.

    django.contrib.auth.Group ya posee los campos
    1. name (descripcion corta)
    2. permissions (many-to-many)
    """
    group = models.OneToOneField( djGroup, on_delete = models.CASCADE, verbose_name = "Grupo" ) #TODO Cuidar eliminación
    desc_larga = models.TextField( "Descripcion larga" )

    def __str__(self):
        dataString = "<{g.name}, desc_larga: {d}>"
        return dataString.format(g=self.group, d=self.desc_larga)
