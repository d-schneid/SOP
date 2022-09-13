from unittest.mock import MagicMock

import django.test

from experiments.management.commands.pyodtodb import Command, _PYOD_ALGORITHMS
from experiments.models import Algorithm
from tests.generic import MediaMixin


class PyodToDBTests(MediaMixin, django.test.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.stdout_write_mock = MagicMock()
        self.cmd.stdout.write = self.stdout_write_mock
        super().setUp()

    def test_pyod_to_db(self) -> None:
        assert Algorithm.objects.all().count() == 0
        self.cmd.handle(quiet=False)
        self.assertEqual(Algorithm.objects.all().count(), len(_PYOD_ALGORITHMS))
        self.assertNotEqual(self.cmd.stdout.write.call_count, 0)

    def test_pyod_to_db_silent(self) -> None:
        assert Algorithm.objects.all().count() == 0
        self.cmd.handle(quiet=True)
        self.assertEqual(Algorithm.objects.all().count(), len(_PYOD_ALGORITHMS))
        self.assertEqual(self.cmd.stdout.write.call_count, 0)

    def test_pyod_to_db_consecutive_calls(self) -> None:
        assert Algorithm.objects.all().count() == 0
        self.cmd.handle(quiet=False)
        algorithm_queryset = list(Algorithm.objects.all())
        self.cmd.handle(quiet=False)
        algorithm_queryset_second = list(Algorithm.objects.all())
        self.cmd.handle(quiet=False)
        algorithm_queryset_third = list(Algorithm.objects.all())
        self.assertListEqual(algorithm_queryset, algorithm_queryset_second)
        self.assertListEqual(algorithm_queryset, algorithm_queryset_third)
