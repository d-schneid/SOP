from unittest.mock import MagicMock

import django.test

from authentication.models import User
from experiments.management.commands.createuser import Command


class MarkCrashedTests(django.test.TestCase):
    already_existing_user: User

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.already_existing_user = User.objects.create_user(
            username="existing", password="passwd"
        )

    def setUp(self) -> None:
        self.data = {
            "username": "new_user",
            "password": "supersecurepassword",
            "staff": False,
            "admin": False,
        }
        self.cmd = Command()
        self.stdout_write_mock = MagicMock()
        self.cmd.stdout.write = self.stdout_write_mock
        super().setUp()

    def test_create_user(self) -> None:
        self.cmd.handle(**self.data)

        self.assertEqual(User.objects.all().count(), 2)
        self.assertIsNotNone(User.objects.get(username=self.data["username"]))

    def test_create_user_already_exists(self) -> None:
        self.data["username"] = "existing"

        self.cmd.handle(**self.data)

        # check that error message was printed
        self.stdout_write_mock.assert_called()
        self.assertTrue("already exists" in str(self.stdout_write_mock.call_args))

        # check that no user was created
        self.assertEqual(User.objects.all().count(), 1)

        # check user privileges
        user = User.objects.get(username=self.data["username"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_admin(self) -> None:
        self.data["admin"] = True

        self.cmd.handle(**self.data)

        self.assertEqual(User.objects.all().count(), 2)

        user = User.objects.get(username=self.data["username"])
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_user_staff(self) -> None:
        self.data["staff"] = True

        self.cmd.handle(**self.data)

        self.assertEqual(User.objects.all().count(), 2)

        user = User.objects.get(username=self.data["username"])
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)
