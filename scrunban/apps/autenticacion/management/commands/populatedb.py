from django.core.management.base import BaseCommand, CommandError

from apps.administracion.models import UserStory
from apps.autenticacion.models import User
from apps.proyecto.models import Project

from apps.autenticacion.apps import AutenticacionConfig

class Command(BaseCommand):
    help = 'Populate database with default data'


    def handle(self, *args, **options):

        # Carga permisos por defectos en caso de no existir
        AutenticacionConfig.get_ready(AutenticacionConfig)

        # Carga usuarios
        self.create_users()

        # Carga proyectos
        self.create_projects()

        self.stdout.write(self.style.SUCCESS('Successfully populated db'))

    def create_users(self):
        usuarios = [
            (
                '1478963',
                'user123',
                'Kishan',
                'Everild',
                'keverild@scrunban.com',
                '0123 456789',
                'South Africa',
            ),
            (
                '1478964',
                'user123',
                'Finnuala',
                'Sylvana',
                'finsyl@scrunban.com',
                '1594 546987',
                'England',
            ),
            (
                '1478965',
                'user123',
                'Aaliyah',
                'Erja',
                'aerja@scrunban.com',
                '548 14588563',
                'India',
            ),
            (
                '1478966',
                'user123',
                'Salomon',
                'Mina',
                'smina@scrunban.com',
                '321 45678975',
                'France',
            ),
            (
                '1478967',
                'user123',
                'Evike',
                'Severe',
                'esevere@scrunban.com',
                '548 17524834',
                'France',
            ),
        ]

        for reg in usuarios:
            User.users.create(username=reg[0],password=reg[1],first_name=reg[2],last_name=reg[3],email=reg[4],telefono=reg[5],direccion=reg[6])


    def create_projects(self):


        proyecots = [
            (
                'Drugdul Project',
                '2016-05-05',
                '2016-06-05',
                '1478963',
                '1478964'
            ),
            (
                'Gordarg Project',
                '2016-05-06',
                '2016-06-06',
                '1478965',
                '1478966'
            ),
            (
                'Uilosdir Project',
                '2016-05-07',
                '2016-06-07',
                '1478967',
                '1478963'
            ),
            (
                'Roston Project',
                '2016-05-08',
                '2016-06-08',
                '1478964',
                '1478965'
            ),
            (
                'Cualnol Project',
                '2016-05-09',
                '2016-06-09',
                '1478966',
                '1478967'
            )

        ]

        for reg in proyecots:

            _t = Project.objects.filter(name=reg[0])
            if (len(_t) != 0):
                _t.delete()

            scrum_master = User.users.filter(username=reg[3])[0]
            product_owner = User.users.filter(username=reg[4])[0]

            p = Project.projects.create(name=reg[0], date_start=reg[1], date_end=reg[2], scrum_master=scrum_master, product_owner=product_owner)

            # Crea User Stories
            if p != None:
                self.create_user_story(p)


    def create_user_story(self, project):

        user_stories = [
            (
                'Creacion de login',
                'Creacion del caso de uso login',
                'Debe funcionar correctamente y pasar todos los tests',
                '3',
                '2.3',
                '3.2',
                '5',
                'FOR ALL PROJECTS',
                'DONT KNOW WHAT THIS IS'
            ),
            (
                'Creacion de Proyecto',
                'Creacion del modelo proyecto',
                'Debe funcionar correctamente y pasar todos los tests',
                '2',
                '2.3',
                '5.2',
                '2',
                'FOR ALL PROJECTS',
                'DONT KNOW WHAT THIS IS'
            ),
            (
                'Creacion de Sprint',
                'Creacion del modelo Sprint',
                'Debe funcionar correctamente y pasar todos los tests',
                '5',
                '3.3',
                '9.2',
                '2',
                'FOR ALL PROJECTS',
                'DONT KNOW WHAT THIS IS'
            ),
            (
                'Creacion de Roles',
                'Creacion del caso de uso roles',
                'Debe funcionar correctamente y pasar todos los tests',
                '3',
                '2.3',
                '7.2',
                '8',
                'FOR ALL PROJECTS',
                'DONT KNOW WHAT THIS IS'
            ),
            (
                'Creacion de vista de asignacion de roles',
                'Creacion del caso de uso asignar rol',
                'Debe funcionar correctamente y pasar todos los tests',
                '4',
                '4.3',
                '3.2',
                '2',
                'FOR ALL PROJECTS',
                'DONT KNOW WHAT THIS IS'
            ),
            (
                'Creacion de vista de eliminacion de usuario',
                'Creacion del caso de uso eliminar usuario',
                'Debe funcionar correctamente y pasar todos los tests',
                '2',
                '7.3',
                '4.2',
                '2',
                'FOR ALL PROJECTS',
                'DONT KNOW WHAT THIS IS'
            ),
            (
                'Creacion de usuario',
                'Creacion del caso de uso crear usuario',
                'Debe funcionar correctamente y pasar todos los tests',
                '3',
                '4.3',
                '5.2',
                '3',
                'FOR ALL PROJECTS',
                'DONT KNOW WHAT THIS IS'
            ),


        ]

        for reg in user_stories:
           us = UserStory()
           us.description = reg[0]
           us.details = reg[1]
           us.acceptance_requirements = reg[2]
           us.estimated_time = reg[3]
           us.business_value = reg[4]
           us.tecnical_value = reg[5]
           us.urgency = reg[6]
           us.project = project

           us.save()
