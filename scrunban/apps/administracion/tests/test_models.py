from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.utils import timezone
from apps.autenticacion.models import User, Role
from apps.administracion.models import Project, ProductBacklog, UserStory, UserStoryNote
import time


class AutenticacionModelsTests(TestCase):
        def create_project(self, nombre='Testing project'):


                u = User.users.create(username='Test_user', password='dummy password')

                data = {
                        'name': nombre,
                        'date_start': time.strftime('%Y-%m-%d'),
                        'date_end': time.strftime('%Y-%m-%d'),
                        'scrum_master': u,
                        'product_owner': u,
                }

                return Project.projects.create(**data)

        def test_project_create_delete(self):

                project = self.create_project()

                project.delete()

        def test_project_create_delete_existing_project(self):

                project1 = self.create_project()
                project2 = self.create_project()

                self.assertNotEqual(project1, None)
                self.assertEqual(project2, None)
                project1.delete()

        def test_project_check_params(self):
                no_nombre = {
                }

                self.assertRaises(KeyError, Project.projects.create, **no_nombre)

        def test_project_check_getters(self):

                project_name = 'Test'
                project = self.create_project(project_name)
                self.assertEqual(project_name, project.get_name())


        def test_project_create_delete_rol_with_name(self):

                rol_data = {
                        'name': 'test_role',
                        'desc_larga': 'Role description',
                }

                project = self.create_project()
                self.assertNotEqual(project, None)

                new_rol = project.add_rol(**rol_data)
                self.assertNotEqual(new_rol, None)

                project_id = project.id
                rol_name = str(project_id) + '_' + rol_data['name']
                self.assertEqual(new_rol.get_name(), rol_name)

                project.remove_rol(new_rol.get_name())

                removed_rol = Role.objects.filter(group__name=rol_name)
                self.assertEqual(len(removed_rol), 0)

                project.delete()

        def test_project_create_delete_rol_without_name(self):

                rol_data = {
                        'desc_larga': 'Role description',
                }

                project = self.create_project()
                self.assertNotEqual(project, None)

                new_rol = project.add_rol(**rol_data)
                self.assertNotEqual(new_rol, None)

                project_id = project.id
                rol_name_starts_with = str(project_id) + '_r_'
                self.assertEqual(new_rol.get_name().startswith(rol_name_starts_with), True)

                rol_name = new_rol.get_name()

                project.remove_rol(new_rol.get_name())

                removed_rol = Role.objects.filter(group__name=rol_name)
                self.assertEqual(len(removed_rol), 0)

                project.delete()

        def test_project_create_delete_existing_rol(self):

                rol_data = {
                        'name': 'test_role',
                        'desc_larga': 'Role description',
                }

                project = self.create_project()
                self.assertNotEqual(project, None)

                new_rol = project.add_rol(**rol_data)
                self.assertNotEqual(new_rol, None)

                new_rol_2 = project.add_rol(**rol_data)
                self.assertEqual(new_rol_2, None)

                new_rol.delete()
                project.delete()

        def test_project_get_role_list(self):

                rol_data_1 = {
                        'name': 'test_role_1',
                        'desc_larga': 'Role description',
                }

                rol_data_2 = {
                        'name': 'test_role_2',
                        'desc_larga': 'Role description',
                }

                rol_data_3 = {
                        'name': 'test_role_3',
                        'desc_larga': 'Role description',
                }

                project = self.create_project()
                self.assertNotEqual(project, None)

                new_rol_1 = project.add_rol(**rol_data_1)
                self.assertNotEqual(new_rol_1, None)
                new_rol_2 = project.add_rol(**rol_data_2)
                self.assertNotEqual(new_rol_2, None)
                new_rol_3 = project.add_rol(**rol_data_3)
                self.assertNotEqual(new_rol_3, None)

                role_list = project.get_roles()
                self.assertEqual(len(role_list), 3)

                new_rol_1.delete()
                new_rol_2.delete()
                new_rol_3.delete()
                project.delete()

        def test_project_get_user_permissions(self):
                user_data = {
                        'username': 'random_nxhOkbjysw',
                        'password': 'pass'
                }


                rol_data_1 = {
                        'name': 'test_role_1',
                        'desc_larga': 'Role description',
                }

                rol_data_2 = {
                        'name': 'test_role_2',
                        'desc_larga': 'Role description',
                }

                permission_data_1 = {
                        'name': 'Permission Description',
                        'codename': 'permission_1',
                        'content_type' : ContentType.objects.get_for_model(Project)
                }

                permission_data_2 = {
                        'name': 'Permission Description',
                        'codename': 'permission_2',
                        'content_type': ContentType.objects.get_for_model(Project)
                }


                user = User.users.create(**user_data)
                self.assertNotEqual(user, None)

                project = self.create_project()
                self.assertNotEqual(project, None)

                rol_1 = project.add_rol(**rol_data_1)
                self.assertNotEqual(rol_1, None)

                rol_2 = project.add_rol(**rol_data_2)
                self.assertNotEqual(rol_2, None)

                perm_1 = Permission.objects.create(**permission_data_1)
                self.assertNotEqual(perm_1, None)

                perm_2 = Permission.objects.create(**permission_data_2)
                self.assertNotEqual(perm_2, None)

                rol_1.add_perm(perm_1)
                self.assertEqual(perm_1 in rol_1.group.permissions.all(), True)

                rol_2.add_perm(perm_2)
                self.assertEqual(perm_2 in rol_2.group.permissions.all(), True)

                rol_1.add_user(user)
                self.assertEqual(rol_1.group in user.user.groups.all(), True)
                perm_list = project.get_user_perms(user)
                self.assertEqual(len(perm_list), 1)
                self.assertEqual(perm_1 in perm_list, True)

                rol_2.add_user(user)
                self.assertEqual(rol_2.group in user.user.groups.all(), True)
                perm_list = project.get_user_perms(user)
                self.assertEqual(len(perm_list), 2)
                self.assertEqual(perm_2 in perm_list, True)

                perm_1.delete()
                perm_2.delete()
                rol_1.delete()
                rol_2.delete()
                project.delete()
                user.delete()

        def test_project_has_perm(self):
                user_data = {
                        'username': 'random_nxhOkbjysw',
                        'password': 'pass'
                }


                rol_data = {
                        'name': 'test_role',
                        'desc_larga': 'Role description',
                }

                permission_data = {
                        'name': 'Permission Description',
                        'codename': 'permission',
                        'content_type': ContentType.objects.get_for_model(Project)
                }

                user = User.users.create(**user_data)
                self.assertNotEqual(user, None)

                project = self.create_project()
                self.assertNotEqual(project, None)

                rol = project.add_rol(**rol_data)
                self.assertNotEqual(rol, None)

                perm = Permission.objects.create(**permission_data)
                self.assertNotEqual(perm, None)

                rol.add_perm(perm)
                self.assertEqual(perm in rol.group.permissions.all(), True)

                rol.add_user(user)
                self.assertEqual(rol.group in user.user.groups.all(), True)
                self.assertEqual(perm in project.get_user_perms(user), True)
                self.assertEqual(project.has_perm(user, permission_data['codename']), True)


                perm.delete()
                rol.delete()
                project.delete()
                user.delete()

        def test_pbacklog_create_delete(self):
                data = {
                        'id' : 155
                }

                pb = ProductBacklog.productbacklogs.create(**data)

                self.assertNotEqual(pb, None)

                pb.delete()

        def test_userstory_create_delete(self):
                data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80
                }

                us = UserStory.objects.create(**data)
                
                self.assertNotEqual(us, None)
                
                us.delete()

        def test_userstory_getters_setters(self):
                data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80
                }
                new_data = {
                        'description': 'New Main Page',
                        'details': 'Make it not like google',
                        'acceptance_requirements': 'Has not to be blue',
                        'deadline': timezone.now(),
                        'business_value': 15,
                        'tecnical_value': 455.8,
                        'urgency': 88
                }

                us = UserStory.objects.create(**data)
                
                self.assertNotEqual(us, None)

                self.assertEqual(us.description, data['description'])
                self.assertEqual(us.details, data['details'])
                self.assertEqual(us.acceptance_requirements, data['acceptance_requirements'])
                self.assertEqual(us.deadline, data['deadline'])
                self.assertEqual(us.business_value, data['business_value'])
                self.assertEqual(us.tecnical_value, data['tecnical_value'])
                self.assertEqual(us.urgency, data['urgency'])

                us.description = new_data['description']
                us.details = new_data['details']
                us.acceptance_requirements = new_data['acceptance_requirements']
                us.business_value = new_data['business_value']
                us.tecnical_value = new_data['tecnical_value']
                us.urgency = new_data['urgency']

                self.assertEqual(us.description, new_data['description'])
                self.assertEqual(us.details, new_data['details'])
                self.assertEqual(us.acceptance_requirements, new_data['acceptance_requirements'])
                self.assertEqual(us.business_value, new_data['business_value'])
                self.assertEqual(us.tecnical_value, new_data['tecnical_value'])
                self.assertEqual(us.urgency, new_data['urgency'])
                
                us.delete()                
                
        def test_userstorynote_create_delete(self):
                us_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80
                }
                
                us = UserStory.objects.create(**us_data)
                self.assertNotEqual(us, None)
                
                usn_data = {
                        'note': 'This is a note about an user story',
                        'user_story': us
                        }

                usn = UserStoryNote.objects.create(**usn_data)
                self.assertNotEqual(usn, None)
                
                usn.delete()
                us.delete()

        def test_userstorynote_getters_setters(self):
                us1_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80
                }
                us2_data = {
                        'description': 'New Main Page',
                        'details': 'Make it not like google',
                        'acceptance_requirements': 'Has not to be blue',
                        'deadline': timezone.now(),
                        'business_value': 15,
                        'tecnical_value': 455.8,
                        'urgency': 88
                }
                us1 = UserStory.objects.create(**us1_data)
                us2 = UserStory.objects.create(**us2_data)
                self.assertNotEqual(us1, None)
                self.assertNotEqual(us2, None)
                
                usn_data = {
                        'note': 'This is a note',
                        'user_story': us1
                }

                usn = UserStoryNote.objects.create(**usn_data)
                self.assertNotEqual(usn, None)
                
                self.assertEqual(usn.note, usn_data['note'])
                self.assertEqual(usn.user_story, usn_data['user_story'])

                new_note = 'This is a new note'
                usn.note = new_note
                self.assertEqual(usn.note, new_note)

                usn.user_story = us2
                self.assertEqual(usn.user_story, us2)

                usn.delete()
                us1.delete()
                us2.delete()

        def test_userstory_get_userstorynotes(self):
                us_data = {
                        'description': 'Main Page',
                        'details': 'Make it like google',
                        'acceptance_requirements': 'Has to be blue',
                        'deadline': timezone.now(),
                        'business_value': 153.1,
                        'tecnical_value': 45.8,
                        'urgency': 80
                }
                
                us = UserStory.objects.create(**us_data)
                self.assertNotEqual(us, None)
                
                usn1_data = {
                        'note': 'This is a note about an user story',
                        'user_story': us
                }
                usn2_data = {
                        'note': 'This is another note about an user story',
                        'user_story': us
                }

                usn1 = UserStoryNote.objects.create(**usn1_data)
                usn2 = UserStoryNote.objects.create(**usn2_data)
                self.assertNotEqual(usn1, None)
                self.assertNotEqual(usn2, None)
                
                self.assertEqual(usn1 in us.get_notes(), True)
                self.assertEqual(usn2 in us.get_notes(), True)
                
                us.delete()
                self.assertEqual(UserStoryNote.objects.all().count(), 0)
