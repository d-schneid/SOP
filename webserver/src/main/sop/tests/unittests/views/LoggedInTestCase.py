from django.test import TestCase
from django.urls import reverse

from authentication.models import User


class LoggedInTestCase(TestCase):
    def setUp(self) -> None:
        self.credentials = {"username": "user", "password": "passwd"}
        self.user = User.objects.create_user(**self.credentials)
        self.client.post(reverse("login"), self.credentials, follow=True)
        super().setUp()

class AdminLoggedInTestCase(TestCase):
    def setUp(self) -> None:
        self.credentials = {"username": "admin", "password": "passwd"}
        self.admin = User.objects.create_superuser(**self.credentials)
        self.client.post(reverse("login"), self.credentials, follow=True)
        super().setUp()
