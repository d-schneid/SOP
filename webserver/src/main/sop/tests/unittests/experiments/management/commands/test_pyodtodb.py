import django.test

from experiments.management.commands.pyodtodb import Command
from experiments.models import Algorithm
from tests.generic import MediaMixin


class PyodToDBTests(MediaMixin, django.test.TestCase):
    def test_pyod_to_db(self) -> None:
        assert Algorithm.objects.all().count() == 0
        cmd = Command()
        cmd.handle(quiet=False)
        self.assertEqual(Algorithm.objects.all().count(), 36)
