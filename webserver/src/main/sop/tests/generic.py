import os.path
import shutil
from typing import Dict

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


def _clear_media_root():
    for filename in os.listdir(settings.MEDIA_ROOT):
        file_path = settings.MEDIA_ROOT / filename
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    assert os.path.isdir(settings.MEDIA_ROOT)
    assert len(os.listdir(settings.MEDIA_ROOT)) == 0


class MediaMixin(MixinBase):

    @classmethod
    def setUpClass(cls):
        if not os.path.isdir(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        else:
            _clear_media_root()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def setUp(self):
        if not os.path.isdir(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        super().setUp()

    def tearDown(self):
        super().tearDown()
        if os.path.isdir(settings.MEDIA_ROOT):
            _clear_media_root()



class LoggedInMixin(MixinBase):
    credentials: Dict[str, str]
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


class AdminLoggedInMixin(MixinBase):
    credentials: Dict[str, str]
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
