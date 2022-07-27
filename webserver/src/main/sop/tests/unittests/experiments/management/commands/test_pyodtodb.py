import os
import shutil

import django.test
from django.conf import settings

from experiments.management.commands.pyodtodb import Command
from experiments.models import Algorithm


class PyodToDBTests(django.test.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def test_pyod_to_db(self) -> None:
        cmd = Command()
        cmd.handle()
        self.assertEqual(Algorithm.objects.all().count(), 35)
