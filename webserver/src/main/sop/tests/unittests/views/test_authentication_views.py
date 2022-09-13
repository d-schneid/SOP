import django.test
from django.urls import reverse

from authentication.models import User


class LoginViewTest(django.test.TestCase):

    def test_invalid_login_credentials(self):
        self.credentials = {"username": "user", "password": "passwd"}
        self.user = User.objects.create_user(**self.credentials)
        login_data = {"username": "user", "password": "forgot"}
        response = self.client.post(reverse("login"), login_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "login")
        self.assertContains(response, "Invalid Login")
