from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.utils import timezone
from apps.autenticacion.models import User, Role
from apps.administracion.models import UserStory, Note, Grained
from apps.proyecto.models import Project, Sprint
import time

class AutenticacionModelsTests(TestCase):
        def setUp(self):
                from apps.autenticacion.models import Role, User
                from apps.autenticacion import settings
                from django.contrib.auth.models import Permission
                from django.contrib.contenttypes.models import ContentType

                __user_contenttype = ContentType.objects.get_for_model(User)

                for def_perm in settings.DEFAULT_PERMISSIONS:
                        perm = Permission.objects.filter(codename=def_perm[0])
                        if (len(perm) == 0):
                                permission_data = {
                                        'name': def_perm[1],
                                        'codename': def_perm[0],
                                        'content_type': __user_contenttype
                                }
                                perm = Permission.objects.create(**permission_data)

                for def_rol in settings.DEFAULT_ADMIN_ROLES:
                        rol = Role.roles.filter(name=def_rol[0])
                        if (len(rol) == 0):
                                role_data = {
                                        'name': def_rol[0],
                                        'desc_larga': def_rol[1]
                                }
                                r = Role.roles.create(**role_data)

                                for p in def_rol[2]:
                                        perm = Permission.objects.filter(codename=p[0])[0]
                                        r.add_perm(perm)

        def helper_create_user(self, username):
                return User.users.create(username=username, password=username)
        
        def helper_create_project(self, name, scrum_master, product_owner):
                prj_data = {
                        'name': name,
                        'date_start': time.strftime('%Y-%m-%d'),
                        'date_end': time.strftime('%Y-%m-%d'),
                        'scrum_master': scrum_master,
                        'product_owner': product_owner
                }
                return Project.projects.create(**prj_data)

        def helper_create_sprint(self, project):
                data = {
                        'project': project,
                        'seq': 1,
                        'estimated_time': 1
                }
                return Sprint.sprints.create(**data)

        def helper_create_user_story(self, project, developers):
                us_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'estimated_time': '10',
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': project
                }
                us = UserStory.user_stories.create(**us_data)

                return us
        
        def test_userstory_create_delete(self):
                user1 = self.helper_create_user('user1')
                user2 = self.helper_create_user('user2')
                self.assertNotEqual(user1, None)
                self.assertNotEqual(user2, None)

                prj = self.helper_create_project('Dummy Project', user1, user1)
                self.assertNotEqual(prj, None)
                
                us_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'estimated_time': '10',
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': prj
                }
                us = UserStory.objects.create(**us_data)
                self.assertNotEqual(us, None)
                
                us.delete()
                prj.delete()
                user1.delete()
                user2.delete()

        def test_userstory_getters_setters(self):
                user1 = self.helper_create_user('user1')
                user2 = self.helper_create_user('user2')
                prj1 = self.helper_create_project('Dummy1', user1, user1)
                prj2 = self.helper_create_project('Dummy2', user2, user2)
                
                data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'estimated_time': '10',
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': prj1
                }
                new_data = {
                        'description': 'New Main Page',
                        'details': 'Make it not like google',
                        'acceptance_requirements': 'Has not to be blue',
                        'estimated_time': '10',
                        'business_value': 15,
                        'tecnical_value': 455.8,
                        'urgency': 88,
                        'project': prj2
                }

                us = UserStory.objects.create(**data)
                
                self.assertNotEqual(us, None)

                self.assertEqual(us.description, data['description'])
                self.assertEqual(us.details, data['details'])
                self.assertEqual(us.acceptance_requirements, data['acceptance_requirements'])
                self.assertEqual(us.business_value, data['business_value'])
                self.assertEqual(us.tecnical_value, data['tecnical_value'])
                self.assertEqual(us.urgency, data['urgency'])
                self.assertEqual(us.project, data['project'])

                us.description = new_data['description']
                us.details = new_data['details']
                us.acceptance_requirements = new_data['acceptance_requirements']
                us.business_value = new_data['business_value']
                us.tecnical_value = new_data['tecnical_value']
                us.urgency = new_data['urgency']
                us.project = new_data['project']

                self.assertEqual(us.description, new_data['description'])
                self.assertEqual(us.details, new_data['details'])
                self.assertEqual(us.acceptance_requirements, new_data['acceptance_requirements'])
                self.assertEqual(us.business_value, new_data['business_value'])
                self.assertEqual(us.tecnical_value, new_data['tecnical_value'])
                self.assertEqual(us.urgency, new_data['urgency'])
                self.assertEqual(us.project, new_data['project'])
                
                us.delete()
                prj1.delete()
                prj2.delete()
                user1.delete()
                user2.delete()

        def test_grained_create_delete(self):
                usr1 = self.helper_create_user('user1')
                prj = self.helper_create_project('Dummy', usr1, usr1)
                spr = self.helper_create_sprint(prj)
                us = self.helper_create_user_story(prj, usr1)
                
                data = {
                        'sprint': spr,
                        'user_story': us
                }
                g = Grained.graineds.create(**data)
                self.assertNotEqual(g, None)
                g.delete()
                
        def no_test_note_create_delete(self):
                user1 = self.helper_create_user('user1')
                prj1 = self.helper_create_project('Dummy1', user1, user1)

                us_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'estimated_time': '10',
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': prj1
                }
                
                us = UserStory.objects.create(**us_data)
                self.assertNotEqual(us, None)
                
                usn_data = {
                        'note': 'This is a note about an user story',
                        'user': user1
                }

                usn = Note.notes.create(**usn_data)
                self.assertNotEqual(usn, None)
                
                usn.delete()
                us.delete()

