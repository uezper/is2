from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User as djUser
from django.contrib.auth.models import Permission as djPermission
from django.contrib.auth.models import Group as djGroup

class UserManager(models.Manager):
    #TODO Check in ERS for optional fields...
    #TODO Check for unique username!
    def create(self, **kwargs):
        if self.get(kwargs['username']) is None:
            dj_user = djUser.objects.create( username=kwargs['username'], password=kwargs['password'] )
            dj_user.email      = kwargs.get('email', '')
            dj_user.first_name = kwargs.get('first_name', '')
            dj_user.last_name  = kwargs.get('last_name', '')
            dj_user.save()

            new_user = User._default_manager.create(
                user=dj_user,
                telefono=kwargs.get('telefono', ''),
                direccion=kwargs.get('direccion', '')
            )
            new_user.save()

            return new_user
        else:
            return None

    #TODO Check if no user
    #TODO Extend
    def get(self, username):
        results = [user for user in User._default_manager.all() if user.user.username == username]
        if len(results) == 0:
            return None
        else:
            return results[0]
    


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
    _default_manager = models.Manager()
    user = models.OneToOneField( djUser, verbose_name = "Usuario para Autenticacion")
    telefono = models.TextField( "Telefono" )
    direccion =  models.TextField( "Direccion" )
    objects = UserManager() 

    def __str__(self):
        dataString = "{u.username}, email: {u.email}"
        return dataString.format(u=self.user)

"""
Escucha al evento de eliminación de User para eliminar el django.contrib.auth.models.User asociado.
"""
@receiver(models.signals.post_delete, sender=User, dispatch_uid='user_delete_signal')
def user_delete(sender, instance, *args, **kwargs):
    djUser.objects.get(username=instance.user.username).delete()
    
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
