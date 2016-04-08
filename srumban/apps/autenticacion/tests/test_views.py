from django.test.utils import setup_test_environment
from django.core.urlresolver import reverse

class AutenticationViewTests(TestCase):
	def test_autentication_with_correct_user(self):
		
		
		
		response = self.client(reverse('polls:index'))
		
		
