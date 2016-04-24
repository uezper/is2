from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User as djUser
from django.contrib.auth.models import Group as djGroup
from guardian.shortcuts import assign_perm, get_perms

class UserManager(models.Manager):
    """
    Clase administradora de operaciones a nivel de tabla del modelo ``User''.
    """
    #TODO Check in ERS for optional fields...
    def create(self, **kwargs):
        # TODO Extend docstring for kwargs
        """
        Crea un usuario.

        :returns: En caso de haberse creado, el nuevo usuario. Sino ``None''
        """
        # Checking for required fields
        required_fields = ['username', 'password']
        for key in required_fields:
            if key not in kwargs.keys():
                raise KeyError('{} is required.'.format(key))

        # Checking if username has already been taken
        if self.get(kwargs['username']) is None:
            dj_user = djUser.objects.create(username=kwargs['username'])
            dj_user.set_password(kwargs['password'])
            dj_user.email = kwargs.get('email', '')
            dj_user.first_name = kwargs.get('first_name', '')
            dj_user.last_name = kwargs.get('last_name', '')
            dj_user.save()

            new_user = User.objects.create(
                user=dj_user,
                telefono=kwargs.get('telefono', ''),
                direccion=kwargs.get('direccion', '')
            )
            new_user.save()

            return new_user
        else:
            return None

    #TODO Extend
    def get(self, username):
        results = [user for user in User.objects.all() if user.user.username == username]
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
    # Public fields mapped to DB columns
    user = models.OneToOneField(djUser, verbose_name="Usuario para Autenticacion")
    telefono = models.TextField("Telefono")
    direccion = models.TextField("Direccion")

    # Public fields for simplicity
    objects = models.Manager()
    users = UserManager()

    def __str__(self):
        username = self.user.get_username()
        return "{}".format(username)

@receiver(models.signals.post_delete, sender=User, dispatch_uid='user_delete_signal')
def user_delete(sender, instance, *args, **kwargs):
    """
    Escucha al evento de eliminación de User para eliminar el User de Django asociado.
    """
    instance.user.delete()

class Role(models.Model):
    """
    Este modelo *extiende* (no hereda) el model por defecto de Django:
    ``django.contrib.auth.models.Group``, agregando un campo.

    El model es usado para manejar los roles en el sistema.

    :param id: Id unico
    :param group: Modelo por defecto de Django. Usado con el framework
    :param desc_larga: Descripcion larga de un rol (nombre legible para usuario)

    """
    # TODO Cuidar eliminacion
    group = models.OneToOneField(djGroup, on_delete=models.CASCADE, verbose_name="Grupo")
    desc_larga = models.TextField("Descripcion larga")

    # TODO Add unit test
    def add_user(self, user):
        user.user.groups.add(self.group)

    # TODO Add unit test
    def remove_user(self, user):
        user.user.groups.remove(self.group)

    def __str__(self):
        return "{g.name}, desc_larga: {d}".format(g=self.group, d=self.desc_larga)

class Project(models.Model):
    """
    Dummy project class!!
    """
    name = models.TextField('Project name')

    class Meta:
        default_permissions = () # To explicitly list permissions
        permissions = (
            ('add_project', 'Crea un projecto y asigna el "Scrum Master".'),
            ('delete_project', 'Elimina un projecto.'),
            ('view_project_details', 'Ver detalles del projecto.'),
            ('view_kanbam', 'Ver Kanbam.'),
        )

    def assign_perm(self, perm, user):
        """
        Asigna el permiso ``perm'' sobre la instancia al usuario ``user''

        :param perm: Cadena que identifica el permiso. Ver clase interna Meta de Project.
        :param user: Instancia de User del usuario a quien asignamos el permiso.
        """
        assign_perm(perm, user.user, self)

    def get_perms(self, user):
        """
        Obtiene una lista de todos los permisos de usuario ``user'' sobre la instancia.

        :param user: Instancia de User de quien obtenemos la lista de permisos.
        :returns: La lista de permisos asignados a user sobre la actual instancia.
        """
        return get_perms(user.user, self)

    def __str__(self):
        return "{}".format(self.name)
