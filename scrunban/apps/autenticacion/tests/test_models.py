from django.test import TestCase
from django.test.utils import setup_test_environment
from apps.autenticacion.models import User, Permission

class AutenticacionModelsTests(TestCase):
        def test_user_create_delete_minimal(self):
                data = {
                        'username' : 'random_nxhOkbjysw',
                        'password' : 'pass'
                }
                
                user = User.objects.create(**data)
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
            
            user = User.objects.create( **data )
            self.assertNotEqual(user, None)
            user.delete()

        def test_user_create_delete_existing_user(self):
                data = {
                        'username' : 'random_sK8FNPLKKM',
                        'password' : 'pass',
                }

                user1 = User.objects.create( **data )
                user2 = User.objects.create( **data )
                self.assertNotEqual(user1, None)
                self.assertEqual(user2, None)
                user1.delete()

        def test_user_create_get_delete_existing_user(self):
                data = {
                        'username' : 'random_oLQPgfyHU4',
                        'password' : 'pass',
                }

                user = User.objects.create( **data )
                result = User.objects.get( data['username'] )
                self.assertEqual(user, result)
                user.delete()

        def test_permission_create_delete_minimal(self):
                data = {
                        'codename' : 'perm1',
                        'name'     : 'Permiso 1',
                }

                perm = Permission.objects.create( **data )
                self.assertNotEqual(perm, None)
                perm.delete()

        def test_permission_create_delete_full(self):
                data = {
                        'codename'  : 'perm1',
                        'name'      : 'Permiso 1',
                        'desc_larga': 'Permiso creado para pruebas!',
                }

                perm = Permission.objects.create( **data )
                self.assertNotEqual(perm, None)
                perm.delete()
