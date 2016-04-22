from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import setup_test_environment
from scrunban.settings import base as base_settings

class AutenticacionViewsTests(TestCase):
        def test_login_view(self):
                resp = self.client.get( reverse(base_settings.LOGIN_NAME) )
                self.assertEqual(resp.status_code, 200)
                # TODO Add more!!
