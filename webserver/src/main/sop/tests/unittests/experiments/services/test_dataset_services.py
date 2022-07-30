import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import django.test
from django.conf import settings

from experiments.services.dataset import save_dataset, generate_path_dataset_cleaned


class DatasetServicesTests(django.test.TestCase):
    def setUp(self) -> None:
        self.init_mocks()
        os.makedirs(settings.MEDIA_ROOT)
        super().setUp()

    def tearDown(self) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def init_mocks(self) -> None:
        self.user = MagicMock()
        self.user.pk = 1
        self.content = ["Line 1\n", "Line 2\n", "Last Line"]
        self.file = MagicMock()
        self.file.chunks.return_value = [bytes(line, "utf-8") for line in self.content]

    def test_save_dataset(self) -> None:
        temp_path = save_dataset(self.file)
        self.assertTrue(os.path.exists(temp_path))
        self.assertEqual(
            Path(temp_path).parent,
            settings.MEDIA_ROOT / "datasets" / "temp",
        )
        with open(temp_path, "r") as f:
            self.assertEqual(len([line for line in f]), 3)
            for index, line in enumerate(f):
                self.assertEqual(line, self.content[index])
        os.remove(temp_path)

    def test_generate_path_dataset_cleaned(self) -> None:
        path = settings.MEDIA_ROOT / "dir1" / "dir2" / "file.ext"
        cleaned_path = generate_path_dataset_cleaned(str(path))
        self.assertEqual(cleaned_path, str(path.parent / "file_cleaned.ext"))

    def test_generate_path_dataset_cleaned_multiple_ext(self) -> None:
        path = settings.MEDIA_ROOT / "dir1" / "dir2" / "file.ext.csv.txt"
        cleaned_path = generate_path_dataset_cleaned(str(path))
        # TODO: Is this expected behaviour?
        self.assertEqual(cleaned_path, str(path.parent / "file.ext.csv_cleaned.txt"))
