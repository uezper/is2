from django.core.exceptions import FieldError
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
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        # Checking if username has already been taken
        if djUser.objects.filter(username=kwargs['username']).count() == 0:
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

    def filter(self, **kwargs):
        django_user_fields = ['username', 'email', 'first_name', 'last_name']
        custom_user_fields = ['direccion', 'telefono']
        
        # Check arguments
        accepted_fields = django_user_fields + custom_user_fields
        for key in kwargs.keys():
            if key not in accepted_fields:
                raise FieldError('Cannot resolve {} into field.'.format(key))

        # Construct params
        params = {}
        for key, value in kwargs.items():
            if key not in custom_user_fields:
                new_key = 'user__' + key
                params[new_key] = value
            else:
                params[key] = value

        # Make query and return
        return User.objects.filter(**params)


    #TODO Deprecated, find something like filter
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

    def get_username(self):
        """
        Returns the user username
        """
        return self.user.get_username()

    def get_email(self):
        """
        Returns the user email
        """
        return self.user.email

    def set_email(self, new_email):
        """
        Sets the user email
        """
        self.user.email = new_email
        self.user.save()

    def get_first_name(self):
        """
        Returns the user first name
        """        
        return self.user.first_name

    def set_first_name(self, new_first_name):
        """
        Sets the user first name
        """
        self.user.first_name = new_first_name
        self.user.save()

    def get_last_name(self):
        """
        Returns the user last name
        """
        return self.user.last_name

    def set_last_name(self, new_last_name):
        """
        Sets the user last name
        """
        self.user.last_name = new_last_name
        self.user.save()

    def get_telefono(self):
        """
        Returns the user telephone
        """        
        return self.telefono

    def set_telefono(self, new_telefono):
        """
        Sets the user telephone
        """
        self.telefono = new_telefono
        self.save()

    def get_direccion(self):
        """
        Returns the user address
        """
        return self.direccion

    def set_direccion(self, new_direccion):
        """
        Sets the user address
        """
        self.direccion = new_direccion
        self.save()

    def __str__(self):
        username = self.user.get_username()
        return "{}".format(username)

@receiver(models.signals.post_delete, sender=User, dispatch_uid='user_delete_signal')
def user_delete(sender, instance, *args, **kwargs):
    """
    Escucha al evento de eliminación de User para eliminar el User de Django asociado.
    """
    instance.user.delete()

class RoleManager(models.Manager):
    def create(self, **kwargs):
        # Checking for required fields
        required_fields = ['name']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError("{} is required.".format(required_field))

        # Checking if name has already been taken
        if djGroup.objects.filter(name=kwargs['name']).count() == 0:
            dj_group = djGroup.objects.create(name=kwargs['name'])
            
            new_role = Role.objects.create(
                group=dj_group,
                desc_larga=kwargs.get('desc_larga', 'Sin descripcion.')
            )

            return new_role
        
        else:
            return None

class Role(models.Model):
    """
    Este modelo *extiende* (no hereda) el model por defecto de Django:
    ``django.contrib.auth.models.Group``, agregando un campo.

    El model es usado para manejar los roles en el sistema.

    :param id: Id unico
    :param group: Modelo por defecto de Django. Usado con el framework
    :param desc_larga: Descripcion larga de un rol (nombre legible para usuario)

    """
    # Public fields mapped to DB columns
    group = models.OneToOneField(djGroup, on_delete=models.CASCADE, verbose_name="Grupo")
    desc_larga = models.TextField("Descripcion larga")

    # Public fields for simplicity
    objects = models.Manager()
    roles = RoleManager()
    
    def add_user(self, user):
        """
        Adds the user to this role
        :param user: Instance of autenticacion.models.User
        """
        user.user.groups.add(self.group)

    def remove_user(self, user):
        """
        Removes user from this role
        :param user: Instance of autenticacion.models.User
        """
        user.user.groups.remove(self.group)

    def get_name(self):
        """
        Returns role name
        """
        return self.group.name

    def get_desc(self):
        """
        Returns role description
        """
        return self.desc_larga

    def set_desc(self, new_desc):
        """
        Sets role description
        """
        self.desc_larga = new_desc
        self.save()

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
