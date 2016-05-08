from django.db import models
from apps.autenticacion.models import User, Role
from django.dispatch import receiver

class BacklogManager(models.Manager):
    def create(self, **kwargs):
        """
        Wrapper of the creation function for Product Backlog
        :param kwargs: Product Backlog data.
        :returns: None if the product backlog has been created or
        the instance of the new product backlog.
        """
        # Checking for required fields
        required_fields = ['id']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        # Check if id has been taken
        if Backlog.backlogs.filter(id=kwargs['id']).count() == 0:
            new_pb = Backlog(kwargs['id'])

            return new_pb
        else:
            return None

class Backlog(models.Model):
    # Public fields mapped to DB columns
    id = models.AutoField(primary_key=True)
    
    # Public fields mapped to DB columns
    backlogs = BacklogManager()
    objects = models.Manager()

    def __str__(self):
        return "%d" % self.id



class SprintBacklog(Backlog):
    """
    Clase que maneja los Sprint Backlogs
    """
    def add_user_story(self, user_story):
        """
        Agrega un User Story al Sprint Backlog
        :param user_story: Instancia de UserStory
        """
        if (isinstance(user_story, UserStory)):
            user_story.sprint_backlog = self
        else:
            raise TypeError('user_story debe ser una instancia de UserStory')

    def remove_user_story(self, user_story):
        """
        Quita un User Story del Sprint Backlog
        :param user_story:  Instancia de UserStory
        """
        if (isinstance(user_story, UserStory)):
            user_story.sprint_backlog = None
        else:
            raise TypeError('user_story debe ser una instancia de UserStory')

    def get_user_stories(self):
        """
        Retorna los user stories del Sprint Backlog
        :return: User stories
        """

        return UserStory.objects.filter(sprint_backlog=self)


class ProductBacklog(Backlog):
    """
    Clase que maneja los Product Backlogs
    """
    def add_user_story(self, user_story):
        """
        Agrega un User Story al Product Backlog
        :param user_story: Instancia de UserStory
        """
        if (isinstance(user_story, UserStory)):
            user_story.product_backlog = self
        else:
            raise TypeError('user_story debe ser una instancia de UserStory')

    def remove_user_story(self, user_story):
        """
        Quita un User Story del Product Backlog
        :param user_story:  Instancia de UserStory
        """
        if (isinstance(user_story, UserStory)):
            user_story.product_backlog = None
        else:
            raise TypeError('user_story debe ser una instancia de UserStory')

    def get_user_stories(self):
        """
        Retorna los user stories del Product Backlog
        :return: User stories
        """

        return UserStory.objects.filter(product_backlog=self)


class ProjectManager(models.Manager):
    def create(self, **kwargs):
        """
        Wrapper of the creation function for Project.
        :param kwargs: Project data.
        :returns: None if the project has not been created or
        the instance of the new project.
        """
        # Checking for required fields

        required_fields = ['name', 'date_start', 'date_end', 'scrum_master', 'product_owner']
        for required_field in required_fields:
            if required_field not in kwargs.keys():
                raise KeyError('{} is required.'.format(required_field))

        # Checking if name has already been taken

        if Project.projects.filter(name=kwargs['name']).count() == 0:
            data = {}
            for f in required_fields:
                data[f] = kwargs[f]

            p = Project()
            pb = Backlog()
            pb.save()

            p.name = data['name']
            p.date_start = data['date_start']
            p.date_end = data['date_end']
            p.scrum_master = data['scrum_master']
            p.product_owner = data['product_owner']
            p.product_backlog = pb
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
        return Project.objects.filter(**kwargs)


class Project(models.Model):
    """

    El model se encarga de guardar informacion de todos los proyectos del sistema.

    :param id: Id unico
    :param name: Nombre del proyecto
    :param date_start: Fecha de inicio del proyecto
    :param date_end: Fecha de finalizacion del proyecto
    :param scrum_master: Scrum Master del proyecto
    :param product_owner: Product Owner del proyecto
    :param development_team: Todos los Development Teams del proyecto
    :param product_backlog: Todos los User Stories del proyecto
    :param capacity: Capacidad del Equipo de desarrollo del proyecto
    """
    # Public fields mapped to DB columns
    id = models.AutoField(primary_key=True)
    name = models.TextField('Project name', unique=True)
    date_start = models.DateField()
    date_end = models.DateField()
    scrum_master = models.ForeignKey(User, null=True, related_name='fk_project_scrum_master')
    product_owner = models.ForeignKey(User, null=True, related_name='fk_project_product_owner')
    development_team = models.ManyToManyField(User, related_name='mm_project_development_team')
    product_backlog = models.OneToOneField(Backlog)
    capacity = models.IntegerField(default=0)

    # Public fields for simplicity
    objects = models.Manager()
    projects = ProjectManager()

    def __str__(self):
        return "{}".format(self.name)


    def get_name(self):
        """
        Returns the project name
        """
        return self.name

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


@receiver(models.signals.post_delete, sender=Project, dispatch_uid='project_delete_signal')
def project_delete(sender, instance, *args, **kwargs):
    """
    Escucha al evento de eliminación de Project para eliminar los roles asociados
    """
    for rol in instance.get_roles():
        rol.delete()


class UserStory(models.Model):
    """
    Modelo donde se almacena la información sobre cada actividad a realizar dentro del projecto.
    """
    # Public fields mapped to DB columns
    description = models.CharField(max_length=140) # Twetter..?? XD
    details = models.TextField()
    acceptance_requirements = models.TextField()
    deadline = models.DateTimeField()
    business_value = models.FloatField()
    tecnical_value = models.FloatField()
    urgency = models.FloatField()
    product_backlog = models.ForeignKey(to=ProductBacklog, null=True, blank=True, on_delete=models.CASCADE)
    sprint_backlog = models.ForeignKey(to=SprintBacklog, null=True, blank=True)

    # Public fields for simplicity
    objects = models.Manager()

    def get_notes(self):
        return UserStoryNote.objects.filter(user_story=self)

    def get_weight(self):
        return (self.business_value + self.urgency + 2 * self.tecnical_value)/4
    
    def __str__(self):
        return "{}".format(self.description)
    
class UserStoryNote(models.Model):
    """
    Modelo para almacenar notas sobre un User Story
    """
    note = models.TextField()
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
