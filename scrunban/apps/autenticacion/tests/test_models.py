from django.test import TestCase
from django.test.utils import setup_test_environment

from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from apps.autenticacion.models import User, Role, Project

class AutenticacionModelsTests(TestCase):
        def test_user_create_delete_minimal(self):
                data = {
                        'username' : 'random_nxhOkbjysw',
                        'password' : 'pass'
                }
                
                user = User.users.create(**data)
                self.assertNotEqual(user, None)
                user.delete()
                
        def test_user_create_delete_full(self):
            data = {
                'username'  : 'random_nSEEJrJz7Z',
                'password'  : 'pass',
                'email'     : 'ran@math.com',
                'first_name': 'Leonhard',
                'last_name' : 'Euler',
                'direccion' : 'Suiza',
                'telefono'  : '2718281828'
            }
            
            user = User.users.create( **data )
            self.assertNotEqual(user, None)
            user.delete()

        def test_user_create_delete_existing_user(self):
                data = {
                        'username' : 'random_sK8FNPLKKM',
                        'password' : 'pass',
                }

                user1 = User.users.create(**data)
                user2 = User.users.create(**data)
                self.assertNotEqual(user1, None)
                self.assertEqual(user2, None)
                user1.delete()

        def test_user_check_params(self):
                no_username = {
                        'password':'test_user',
                }
                no_password = {
                        'username':'test_user',
                }
                
                self.assertRaises(KeyError, User.users.create, **no_username)
                self.assertRaises(KeyError, User.users.create, **no_password)

        def test_user_check_auth(self):
                data = {
                        'username' : 'test_user',
                        'password' : 'test_user',
                }
                wrong_data = {
                        'username' : 'test_user',
                        'password' : 'wrong_password!',
                }
                
                user = User.users.create(**data)
                self.assertNotEqual(authenticate(**data), None)
                self.assertEqual(authenticate(**wrong_data), None)
                user.delete()

        def test_user_check_getters(self):
                data = {
                        'username' : 'test_user',
                        'password' : 'password',
                        'first_name' : 'Test',
                        'last_name': 'User',
                        'email' : 'email@email.com',
                        'direccion' : 'Place',
                        'telefono' : '1122334455',
                }
                user = User.users.create(**data)
                self.assertEqual(data['username'], user.get_username())
                self.assertEqual(data['email'], user.get_email())
                self.assertEqual(data['first_name'], user.get_first_name())
                self.assertEqual(data['last_name'], user.get_last_name())
                self.assertEqual(data['direccion'], user.get_direccion())
                self.assertEqual(data['telefono'], user.get_telefono())
                user.delete()
                
        def test_user_check_getters_setters(self):
                data = {
                        'username' : 'test_user',
                        'password' : 'password',
                        'first_name' : 'Test',
                        'last_name': 'User',
                        'email' : 'email@email.com',
                        'direccion' : 'Place',
                        'telefono' : '1122334455',
                }
                new_data = {
                        'first_name' : 'new_name',
                        'last_name': 'new_last_name',
                        'email' : 'new_email@email.com',
                        'direccion' : 'new_place',
                        'telefono' : '5544332211',                        
                        }
                
                user = User.users.create(**data)
                user.set_email(new_data['email'])
                self.assertEqual(new_data['email'], user.get_email())
                user.set_first_name(new_data['first_name'])
                self.assertEqual(new_data['first_name'], user.get_first_name())
                user.set_last_name(new_data['last_name'])
                self.assertEqual(new_data['last_name'], user.get_last_name())
                user.set_direccion(new_data['direccion'])
                self.assertEqual(new_data['direccion'], user.get_direccion())
                user.set_telefono(new_data['telefono'])
                self.assertEqual(new_data['telefono'], user.get_telefono())
                user.delete()

        def test_user_custom_filter_method(self):
                data = {
                        'username' : 'test_user',
                        'password' : 'password',
                        'first_name' : 'Test',
                        'last_name': 'User',
                        'email' : 'email@email.com',
                        'direccion' : 'Place',
                        'telefono' : '1122334455',
                }
                user = User.users.create(**data)
                
                username_query = User.users.filter(username=data['username'])
                self.assertEqual(username_query.exists(), True)

                first_name_query = User.users.filter(first_name=data['first_name'])
                self.assertEqual(first_name_query.exists(), True)
                
                last_name_query = User.users.filter(last_name=data['last_name'])
                self.assertEqual(last_name_query.exists(), True)

                email_query = User.users.filter(email=data['email'])
                self.assertEqual(email_query.exists(), True)
                
                direccion_query = User.users.filter(direccion=data['direccion'])
                self.assertEqual(direccion_query.exists(), True)

                telefono_query = User.users.filter(telefono=data['telefono'])
                self.assertEqual(telefono_query.exists(), True)

                username_and_email_query = User.users.filter(username=data['username'],
                                                             email=data['email'])
                self.assertEqual(username_and_email_query.exists(), True)
                
                user.delete()        
                
        def test_role_create_delete(self):
                data = {
                        'name' : 'test_role',
                        'desc_larga' : 'Hi!, I am a role!',
                }

                role = Role.roles.create(**data)
                self.assertNotEqual(role, None)
                role.delete()

        def test_role_create_delete_existing_role(self):
                data = {
                        'name' : 'test_role',
                        'desc_larga' : 'Role description',
                }
                
                role1 = Role.roles.create(**data)
                role2 = Role.roles.create(**data)
                self.assertNotEqual(role1, None)
                self.assertNotEqual(role1, role2)
                self.assertEqual(role2, None)
                role1.delete()

        def test_role_check_params(self):
                no_name = {
                        'desc_larga' : 'Role description',
                }
                
                self.assertRaises(KeyError, Role.roles.create, **no_name)
                
        def test_role_check_getters(self):
                data = {
                        'name' : 'test_role',
                        'desc_larga' : 'Role description',
                }

                role = Role.roles.create(**data)
                self.assertEqual(data['name'], role.get_name())
                self.assertEqual(data['desc_larga'], role.get_desc())
                role.delete()
                
        def test_role_check_getters_setters(self):
                data = {
                        'name' : 'test_role',
                        'desc_larga' : 'Role description',
                }
                new_data = {
                        'desc_larga' : 'new description',
                }

                role = Role.roles.create(**data)
                role.set_desc(new_data['desc_larga'])
                self.assertEqual(role.get_desc(), new_data['desc_larga'])
                role.delete()

        def test_role_add_user(self):
                user_data = {
                        'username' : 'test_user',
                        'password' : 'test_user',
                }
                role_data = {
                        'name' : 'test_role',
                }

                user = User.users.create(**user_data)
                role = Role.roles.create(**role_data)

                role.add_user(user)

                self.assertEqual( role.group in user.user.groups.all(), True )
                
                user.delete()
                role.delete()

                
        def test_role_add_remove_user(self):
                user_data = {
                        'username' : 'test_user',
                        'password' : 'test_user',
                }
                role_data = {
                        'name' : 'test_role',
                }

                user = User.users.create(**user_data)
                role = Role.roles.create(**role_data)

                role.add_user(user)
                self.assertEqual( role.group in user.user.groups.all(), True )
                role.remove_user(user)
                self.assertEqual( role.group in user.user.groups.all(), False )
                
                user.delete()
                role.delete()

        def test_role_custom_filter_method(self):
                data = {
                        'name' : 'Role',
                }
                
                role = Role.roles.create(**data)

                name_query = Role.roles.filter(name=data['name'])
                self.assertEqual(name_query.exists(), True)

                role.delete()

        def test_rol_get_users(self):

                user_data_1 = {
                        'username': 'random_nxhOkbjysw_1',
                        'password': 'pass'
                }

                user_data_2 = {
                        'username': 'random_nxhOkbjysw_2',
                        'password': 'pass'
                }

                rol_data = {
                        'name': 'test_role_2',
                        'desc_larga': 'Role description',
                }

                user_1 = User.users.create(**user_data_1)
                self.assertNotEqual(user_1, None)

                user_2 = User.users.create(**user_data_2)
                self.assertNotEqual(user_2, None)

                rol = Role.roles.create(**rol_data)
                self.assertNotEqual(rol, None)

                rol.add_user(user_1)
                self.assertEqual(rol.group in user_1.user.groups.all(), True)

                rol.add_user(user_2)
                self.assertEqual(rol.group in user_2.user.groups.all(), True)

                user_list = rol.get_users()
                self.assertEqual(len(user_list), 2)
                self.assertEqual(user_1 in user_list, True)
                self.assertEqual(user_2 in user_list, True)

                rol.delete()
                user_1.delete()
                user_2.delete()


        def test_role_get_perms(self):

                rol_data = {
                        'name': 'test_role_2',
                        'desc_larga': 'Role description',
                }

                permission_data_1 = {
                        'name': 'Permission Description',
                        'codename': 'permission_1',
                        'content_type': ContentType.objects.get_for_model(Project)
                }

                permission_data_2 = {
                        'name': 'Permission Description',
                        'codename': 'permission_2',
                        'content_type': ContentType.objects.get_for_model(Project)
                }

                rol = Role.roles.create(**rol_data)
                self.assertNotEqual(rol, None)

                perm_1 = Permission.objects.create(**permission_data_1)
                rol.add_perm(perm_1)
                self.assertEqual(perm_1 in rol.group.permissions.all(), True)

                perm_2 = Permission.objects.create(**permission_data_2)
                rol.add_perm(perm_2)
                self.assertEqual(perm_1 in rol.group.permissions.all(), True)

                perm_list = rol.get_perms()

                self.assertEqual(len(perm_list), 2)
                self.assertEqual(perm_1 in perm_list, True)
                self.assertEqual(perm_2 in perm_list, True)

                perm_1.delete()
                perm_2.delete()
                rol.delete()


        def test_project_create_delete(self):
                data = {
                        'name' : 'Project',
                }

                project = Project.projects.create(**data)
                self.assertNotEqual(project, None)
                project.delete()

        def test_project_create_delete_existing_project(self):
                data = {
                        'name' : 'Project',
                }

                project1 = Project.projects.create(**data)
                project2 = Project.projects.create(**data)
                self.assertNotEqual(project1, None)
                self.assertEqual(project2, None)
                project1.delete()

        def test_project_check_params(self):
                no_name = {
                }

                self.assertRaises(KeyError, Project.projects.create, **no_name)

        def test_project_check_getters(self):
                data = {
                        'name' : 'Project',
                }

                project = Project.projects.create(**data)
                self.assertEqual(data['name'], project.get_name())

        def test_project_check_perm_assignment(self):
                user_data = {
                        'username' : 'user_test',
                        'password' : 'password',
                }
                project_data = {
                        'name' : 'project',
                }
                # TODO Improve somehow... TT_TT
                # Probably using Project._meta.permissions..??
                perm_codename = 'view_kanbam'

                user = User.users.create(**user_data)
                project = Project.projects.create(**project_data)

                self.assertNotEqual(user, None)
                self.assertNotEqual(project, None)

                project.assign_perm(perm_codename, user)

                user_perms = project.get_perms(user)
                self.assertEqual(perm_codename in user_perms, True)

                user.delete()
                project.delete()

        def test_project_create_delete_rol_with_name(self):
                project_data = {
                        'name': 'project',
                }

                rol_data = {
                        'name': 'test_role',
                        'desc_larga': 'Role description',
                }

                project = Project.projects.create(**project_data)
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
                project_data = {
                        'name': 'project',
                }

                rol_data = {
                        'desc_larga': 'Role description',
                }

                project = Project.projects.create(**project_data)
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
                project_data = {
                        'name': 'project',
                }

                rol_data = {
                        'name': 'test_role',
                        'desc_larga': 'Role description',
                }

                project = Project.projects.create(**project_data)
                self.assertNotEqual(project, None)

                new_rol = project.add_rol(**rol_data)
                self.assertNotEqual(new_rol, None)

                new_rol_2 = project.add_rol(**rol_data)
                self.assertEqual(new_rol_2, None)

                new_rol.delete()
                project.delete()

        def test_project_get_role_list(self):
                project_data = {
                        'name': 'project',
                }

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

                project = Project.projects.create(**project_data)
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

                project_data = {
                        'name': 'project',
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

                project = Project.projects.create(**project_data)
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

                project_data = {
                        'name': 'project',
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

                project = Project.projects.create(**project_data)
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


