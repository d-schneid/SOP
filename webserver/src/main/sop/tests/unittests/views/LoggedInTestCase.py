from django.test import TestCase
from django.urls import reverse

from authentication.models import User
from backend.scheduler.Scheduler import Scheduler


class DjangoTestCase(TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if Scheduler._instance is not None:
            Scheduler._instance.hard_shutdown()
        super(DjangoTestCase, cls).tearDownClass()


class LoggedInTestCase(DjangoTestCase):
    def setUp(self) -> None:
        self.credentials = {"username": "user", "password": "passwd"}
        self.user = User.objects.create_user(**self.credentials)
        self.client.post(reverse("login"), self.credentials, follow=True)
        super().setUp()


class AdminLoggedInTestCase(DjangoTestCase):
    def setUp(self) -> None:
        self.credentials = {"username": "admin", "password": "passwd"}
        self.admin = User.objects.create_superuser(**self.credentials)
        self.client.post(reverse("login"), self.credentials, follow=True)
        super().setUp()
