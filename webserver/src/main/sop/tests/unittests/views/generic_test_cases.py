from django.test import TestCase
from django.urls import reverse

from authentication.models import User
from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler


class DebugSchedulerTestCase(TestCase):
    """
    This is a generic django.test.TestCase subclass which every of our own TestCase classes should inherit from.
    It handles the creation and shutdown of the DebugScheduler for the backend so the Scheduling will not be
    performed in another process/thread
    """

    @classmethod
    def setUpClass(cls) -> None:
        if Scheduler._instance is not None:
            Scheduler._instance.hard_shutdown()
            Scheduler._instance = None
        DebugScheduler()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        if Scheduler._instance is not None:
            Scheduler._instance.hard_shutdown()
        super().tearDownClass()


class LoggedInTestCase(DebugSchedulerTestCase):
    """
    A DebugSchedulerTestCase subclass which handles the creation of a user and the automatic login of that user before
    running the tests.
    """

    credentials: dict[str, str]
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.credentials = {"username": "user", "password": "passwd"}
        cls.user = User.objects.create_user(**cls.credentials)
        super().setUpTestData()

    def setUp(self) -> None:
        self.client.post(reverse("login"), self.credentials, follow=True)
        super().setUp()


class AdminLoggedInTestCase(DebugSchedulerTestCase):
    """
    A DebugSchedulerTestCase subclass which handles the creation of an admin user and the automatic login of that admin
    before running the tests.
    """

    credentials: dict[str, str]
    admin: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.credentials = {"username": "admin", "password": "passwd"}
        cls.admin = User.objects.create_superuser(**cls.credentials)
        super().setUpTestData()

    def setUp(self) -> None:
        self.client.post(reverse("login"), self.credentials, follow=True)
        super().setUp()
