from django.test import TestCase
from django.test.utils import setup_test_environment
from apps.autenticacion.models import User

class AutenticacionModelsTests(TestCase):
        def test_user_create_delete_minimal(self):
                data = {
                        'username' : 'random_nxhOkbjysw',
                        'password' : 'pass'
                }
                
                User.objects.create(**data)
                result = User.objects.get( data['username'] )
                self.assertNotEqual(result, None)
                result.delete()
                
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
            
            User.objects.create( **data )
            result = User.objects.get( data['username'] )
            self.assertNotEqual(result, None)
            result.delete()

        def test_user_create_delete_existing_user(self):
                data = {
                        'username' : 'user1_sK8FNPLKKM',
                        'password' : 'pass'
                }

                user1 = User.objects.create( **data )
                user2 = User.objects.create( **data )
                self.assertNotEqual(user1, None)
                self.assertEqual(user2, None)
                user1.delete()
