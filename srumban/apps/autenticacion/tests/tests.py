from django.test import TestCase
from django.test.utils import setup_test_environment
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from apps.autenticacion import views

class AutenticationViewTests(TestCase):
	def test_restricted_area_app(self):
		response = self.client.get(reverse('auth:app'))
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/auth/#?next=/auth/app/')
		

