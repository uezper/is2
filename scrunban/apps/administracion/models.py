from django.db import models
from apps.autenticacion.models import User, Role

# Create your models here.


class ProductBacklog(models.Model):
    id = models.AutoField(primary_key=True)
    def __str__(self):
        return "%d" % self.id

class SprintBacklog(models.Model):
    id = models.AutoField(primary_key=True)
    def __str__(self):
        return "%d" % self.id



class ProjectManager(models.Manager):
    def create(self, **kwargs):
        """
        Wrapper of the creation function for Project.
        :param kwargs: Project data.
        :returns: None if the project has not been created or
        the instance of the new project.
        """
        # Checking for required fields
        required_fields = ['nombre', 'fechaInicio', 'fechaFinal', 'scrumMaster', 'productOwner']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        # Checking if name has already been taken
        if Proyecto.projects.filter(nombre=kwargs['nombre']).count() == 0:
            data = {}
            for f in required_fields:
                data[f] = kwargs[f]

            p = Proyecto()
            pb = ProductBacklog()
            pb.save()

            p.nombre = data['nombre']
            p.fechaInicio = data['fechaInicio']
            p.fechaFinal = data['fechaFinal']
            p.scrumMaster = data['scrumMaster']
            p.productOwner = data['productOwner']
            p.productBacklog = pb
            p.save()

            return p


        else:
            return None

    def filter(self, **kwargs):
        """
        Returns the results of a query.
        :param kwargs: Query details.
        :returns: An instance of QuerySet containing the results of the query.
        """
        return Proyecto.objects.filter(**kwargs)



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

    # Public fields for simplicity
    objects = models.Manager()
    projects = ProjectManager()

    def __str__(self):
        return "%s" % self.nombre

    def get_name(self):
        """
        Returns the project name
        """
        return self.nombre

    def add_rol(self, **kwargs):
        """

        Crea un rol de proyecto con un nombre de la forma ``idProyecto_name`` si es que ``name`` es especificado,
         de lo contrario el nombre queda de la forma ``idProyecto_r_num`` donde ``num`` va aumentando secuencialmente.


        :param desc_larga:  Descripcion larga del Rol
        :param name:  Nombre en codigo del Rol
        :returns: Instancia del nuevo rol creado
        """

        required_fields = ['desc_larga']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        p_id = self.id
        r_name = ''

        if ('name' not in kwargs.keys()):
            r_tot = Role.objects.filter(group__name__startswith=str(p_id) + '_r_')
            if (len(r_tot) == 0):
                r_name = str(p_id) + '_r_0'
            else:
                r_last = r_tot.last().get_name()
                r_last = int(r_last[len(r_last) - 1]) + 1
                r_name = str(p_id) + '_r_' + str(r_last)
        else:
            r_name = str(p_id) + '_' + kwargs['name']

        data = {
            'name': r_name,
            'desc_larga': kwargs['desc_larga'],

        }
        new_rol = Role.roles.create(**data)
        return new_rol

    def remove_rol(self, short_name):
        """

        Remueve un rol de un proyecto

        :param short_name: Nombre en codigo del Rol
        """

        p_id = self.id
        Role.objects.filter(group__name=short_name)[0].delete()

    def get_roles(self):

        """

        Obtiene una lista de todos los roles asociados con el proyecto

        :returns: Una lista de roles
        """

        p_id = self.id
        roles = Role.objects.filter(group__name__startswith=str(p_id) + '_')

        return roles

    def get_user_perms(self, user):
        """

        Obtiene una lista de todos los permisos de un Usuario asociados al proyecto a traves de algun rol

        :param user: Instancia de usuario
        :returns: Lista de permisos
        """
        p_id = self.id
        roles = user.user.groups.filter(name__startswith=str(p_id) + '_')

        perms = []

        for rol in roles:
            perms += rol.permissions.all()

        return perms

    def has_perm(self, user, perm):
        """

        Verifica si un usuario tiene un permiso dado dentro de un proyecto

        :param user: Instancia de usuario que se va a verificar que tenga el permiso
        :param perm: Permiso que se desea verificar en su nombre en codigo
        :return:
        """

        for p in self.get_user_perms(user):
            if (p.codename == perm):
                return True

        return False


class Sprint(models.Model):
    id = models.AutoField(primary_key=True)
    sprint = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    def __str__(self):
        return "%d" % self.id

