import os
from unittest import skipIf

import django.test

from experiments.management.commands.pyodtodb import Command
from experiments.models import Algorithm
from tests.generic import MediaMixin


class PyodToDBTests(MediaMixin, django.test.TestCase):
    @skipIf(
        os.environ.get("DJANGO_SETTINGS_MODULE") == "sop.settings_ci",
        "We skip the pyodtodb django admin-command since it needs very big dependencies",
    )
    def test_pyod_to_db(self) -> None:
        cmd = Command()
        cmd.handle()
        self.assertEqual(Algorithm.objects.all().count(), 35)
