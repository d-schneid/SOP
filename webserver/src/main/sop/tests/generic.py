import os.path
import shutil

from django.conf import settings
from django.urls import reverse

from authentication.models import User
from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler


class MixinBase:
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()


class DebugSchedulerMixin(MixinBase):
    @classmethod
    def setUpClass(cls) -> None:
        Scheduler.default_scheduler = DebugScheduler
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        if Scheduler._instance is not None:
            Scheduler.get_instance().hard_shutdown()
            Scheduler._instance = None


class MediaMixin(MixinBase):
    @classmethod
    def setUpClass(cls):
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)


class LoggedInMixin(MixinBase):
    credentials: dict[str, str]
    user: User
    logged_in: bool = False

    @classmethod
    def setUpTestData(cls):
        cls.credentials = {"username": "user", "password": "passwd"}
        cls.user = User.objects.create_user(**cls.credentials)
        super().setUpTestData()

    def setUp(self):
        if not self.logged_in:
            self.client.post(reverse("login"), self.credentials, follow=True)
            self.logged_in = True
        super().setUp()


class MaliciousMixin(MixinBase):
    victim_credentials: dict[str, str]
    victim_user: User

    hacker_credentials: dict[str, str]
    hacker_user: User

    @classmethod
    def setUpTestData(cls):
        cls.victim_credentials = {"username": "victim", "password": "passwd"}
        cls.victim_user = User.objects.create_user(**cls.victim_credentials)

        cls.hacker_credentials = {"username": "hackerman", "password": "1337"}
        cls.hacker_user = User.objects.create_user(**cls.hacker_credentials)
        super().setUpTestData()


class AdminLoggedInMixin(MixinBase):
    credentials: dict[str, str]
    user: User
    logged_in: bool = False

    @classmethod
    def setUpTestData(cls):
        cls.credentials = {"username": "admin", "password": "passwd"}
        cls.admin = User.objects.create_superuser(**cls.credentials)
        super().setUpTestData()

    def setUp(self):
        if not self.logged_in:
            self.client.post(reverse("login"), self.credentials, follow=True)
            self.logged_in = True
        super().setUp()
