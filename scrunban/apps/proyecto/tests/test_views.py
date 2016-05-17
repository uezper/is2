from django.core.urlresolvers import reverse
from django import http
from django.test import TestCase
from scrunban.settings import base as base_settings
from apps.autenticacion.models import User
from apps.administracion.models import Project
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import time

class AutenticacionViewsTests(TestCase):
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

        def authenticate(self, client):
                u = User.users.create(username='Test_client_user', password='client')
                client.login(username='Test_client_user', password='client')

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

        def test_list_rol_view_invalid_project_id(self):
                c = self.client
                self.authenticate(c)

                id = '0'
                path = reverse(base_settings.PROJECT_ROLE_LIST, args=(id,))

                self.assertEqual(isinstance(c.get(path), http.HttpResponseNotFound), True)

        def test_list_rol_view_valid_project(self):
                c = self.client
                self.authenticate(c)

                project = self.create_project()
                self.assertNotEqual(project, None)

                path = reverse(base_settings.PROJECT_ROLE_LIST, args=(project.id,))

                self.assertEqual(c.get(path).status_code, 200)

        def test_create_rol_view_invalid_project(self):
                c = self.client
                self.authenticate(c)

                id = '0'
                path = reverse(base_settings.PROJECT_ROLE_CREATE, args=(id,))

                self.assertEqual(isinstance(c.get(path), http.HttpResponseNotFound), True)

        def test_create_rol_view_invalid_data(self):
                c = self.client
                self.authenticate(c)

                project = self.create_project()
                self.assertNotEqual(project, None)

                path = reverse(base_settings.PROJECT_ROLE_CREATE, args=(project.id,))

                self.assertEqual(len(c.post(path).context_data['form'].errors), 3)

                data = {
                       'projectID': '0',
                }

                self.assertEqual(len(c.post(path, data=data).context_data['form'].errors), 3)

                data = {
                        'projectID': project.id,
                        'inputNombre': 'test_rol',
                        'inputPerms': '0',
                        'inputUsers': '0',
                }

                self.assertEqual(len(c.post(path, data=data).context_data['form'].errors), 2)

        def test_create_rol_view_valid_data(self):
                c = self.client
                self.authenticate(c)

                user_data = {
                        'username': 'random_nxhOkbjysw',
                        'password': 'pass'
                }


                perm_data = {
                        'name' : 'testing perm',
                        'codename' : 'testing_perm',
                        'content_type': ContentType.objects.get_for_model(Permission),
                }

                project = self.create_project()
                self.assertNotEqual(project, None)

                path = reverse(base_settings.PROJECT_ROLE_CREATE, args=(project.id,))

                user = User.users.create(**user_data)
                self.assertNotEqual(user, None)


                perm = Permission.objects.create(**perm_data)
                self.assertNotEqual(perm, None)

                data = {
                        'projectID': project.id,
                        'inputNombre': 'test_rol',
                        'inputPerms': perm.codename,
                        'inputUsers': user.id,
                }

                self.assertEqual(c.post(path, data=data).url, reverse(base_settings.PROJECT_ROLE_LIST, args=(project.id,)))

                rol = None
                for r in project.get_roles():
                        if r.get_desc() == data['inputNombre']:
                                rol = r

                self.assertNotEqual(rol, None)
