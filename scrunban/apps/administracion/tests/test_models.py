from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.utils import timezone
from apps.autenticacion.models import User, Role
from apps.administracion.models import UserStory, Note
from apps.proyecto.models import Project
import time

class AutenticacionModelsTests(TestCase):
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
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': prj
                }
                us = UserStory.objects.create(**us_data)
                us.allowed_developers.add(user1, user2)
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
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': prj1
                }
                new_data = {
                        'description': 'New Main Page',
                        'details': 'Make it not like google',
                        'acceptance_requirements': 'Has not to be blue',
                        'deadline': timezone.now(),
                        'business_value': 15,
                        'tecnical_value': 455.8,
                        'urgency': 88,
                        'project': prj2
                }

                us = UserStory.objects.create(**data)
                us.allowed_developers.add(user1)
                
                self.assertNotEqual(us, None)

                self.assertEqual(us.description, data['description'])
                self.assertEqual(us.details, data['details'])
                self.assertEqual(us.acceptance_requirements, data['acceptance_requirements'])
                self.assertEqual(us.deadline, data['deadline'])
                self.assertEqual(us.business_value, data['business_value'])
                self.assertEqual(us.tecnical_value, data['tecnical_value'])
                self.assertEqual(us.urgency, data['urgency'])
                self.assertEqual(user1 in us.allowed_developers.all(), True)
                self.assertEqual(us.project, data['project'])

                us.description = new_data['description']
                us.details = new_data['details']
                us.acceptance_requirements = new_data['acceptance_requirements']
                us.business_value = new_data['business_value']
                us.tecnical_value = new_data['tecnical_value']
                us.urgency = new_data['urgency']
                us.allowed_developers.add(user2)
                us.project = new_data['project']

                self.assertEqual(us.description, new_data['description'])
                self.assertEqual(us.details, new_data['details'])
                self.assertEqual(us.acceptance_requirements, new_data['acceptance_requirements'])
                self.assertEqual(us.business_value, new_data['business_value'])
                self.assertEqual(us.tecnical_value, new_data['tecnical_value'])
                self.assertEqual(us.urgency, new_data['urgency'])
                self.assertEqual(user2 in us.allowed_developers.all(), True)
                self.assertEqual(us.project, new_data['project'])
                
                us.delete()
                prj1.delete()
                prj2.delete()
                user1.delete()
                user2.delete()
                
        def test_note_create_delete(self):
                user1 = self.helper_create_user('user1')
                prj1 = self.helper_create_project('Dummy1', user1, user1)

                us_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': prj1
                }
                
                us = UserStory.objects.create(**us_data)
                us.allowed_developers.add(user1)
                self.assertNotEqual(us, None)
                
                usn_data = {
                        'note': 'This is a note about an user story',
                        'user_story': us,
                        'user': user1
                }

                usn = Note.notes.create(**usn_data)
                self.assertNotEqual(usn, None)
                
                usn.delete()
                us.delete()

        def test_userstory_get_userstorynotes(self):
                user1 = self.helper_create_user('user1')
                prj = self.helper_create_project('Dummy', user1, user1)
                us_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80,
                        'project': prj
                }
                
                us = UserStory.user_stories.create(**us_data)
                self.assertNotEqual(us, None)
                
                usn1_data = {
                        'note': 'This is a note about an user story',
                        'user_story': us,
                        'user': user1
                }
                usn2_data = {
                        'note': 'This is another note about an user story',
                        'user_story': us,
                        'user': user1
                }

                usn1 = Note.notes.create(**usn1_data)
                usn2 = Note.notes.create(**usn2_data)
                self.assertNotEqual(usn1, None)
                self.assertNotEqual(usn2, None)
                
                self.assertEqual(usn1 in us.get_notes(), True)
                self.assertEqual(usn2 in us.get_notes(), True)
                
                us.delete()
                self.assertEqual(Note.notes.all().count(), 0)
