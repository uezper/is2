from django.test import TestCase
from django.test.utils import setup_test_environment

from django.contrib.auth import authenticate
from apps.autenticacion.models import User

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

                user1 = User.users.create( **data )
                user2 = User.users.create( **data )
                self.assertNotEqual(user1, None)
                self.assertEqual(user2, None)
                user1.delete()

        def test_user_create_get_delete_existing_user(self):
                data = {
                        'username' : 'random_oLQPgfyHU4',
                        'password' : 'pass',
                }

                user = User.users.create( **data )
                result = User.users.get( data['username'] )
                self.assertEqual(user, result)
                user.delete()

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
