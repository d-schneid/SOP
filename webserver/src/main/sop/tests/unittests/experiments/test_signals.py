import os.path
from pathlib import Path
from unittest import mock

import django.test
from django.conf import settings

from experiments.models.execution import get_result_path
from experiments.signals import _delete_file, delete_dataset_file, \
    delete_algorithm_file, delete_result_file  # noqa
from tests.generic import MediaMixin


class TestSignalHandler(MediaMixin, django.test.TestCase):
    def test_delete_file_last_file(self):
        # create file
        path = settings.MEDIA_ROOT / "test.txt"
        with open(path, "w") as f:
            f.write("data")

        self.assertTrue(os.path.isdir(path.parent))
        _delete_file(path)
        self.assertFalse(os.path.isdir(path.parent))

    def test_delete_file_two_files(self):
        # create files
        path1 = settings.MEDIA_ROOT / "test1.txt"
        path2 = settings.MEDIA_ROOT / "test2.txt"
        with open(path1, "w") as f:
            f.write("data")
        with open(path2, "w") as f:
            f.write("data")

        self.assertTrue(os.path.isdir(path1.parent))
        _delete_file(path1)
        self.assertTrue(os.path.isdir(path2.parent))
        self.assertTrue(os.path.isfile(path2))

    def test_dataset_delete_signal(self):
        path_uncleaned = settings.DATASET_ROOT_DIR / "test_dir" / "uncleaned.csv"
        path_cleaned = settings.DATASET_ROOT_DIR / "test_dir" / "cleaned.csv"
        os.makedirs(path_cleaned.parent)
        with open(path_uncleaned, "w") as f:
            f.write("uncleaned_data")
        with open(path_cleaned, "w") as f:
            f.write("cleaned_data")

        dataset = mock.MagicMock()
        dataset.path_original.path = str(path_uncleaned)
        dataset.path_cleaned.path = str(path_cleaned)
        delete_dataset_file(dataset, dataset)
        self.assertFalse(os.path.isfile(path_uncleaned))
        self.assertFalse(os.path.isfile(path_cleaned))
        self.assertFalse(os.path.isdir(path_uncleaned.parent))
        self.assertTrue(os.path.isdir(settings.DATASET_ROOT_DIR))

    def test_algorithm_delete_signal(self):
        algorithm_path = settings.ALGORITHM_ROOT_DIR / "test_dir" / "algo.py"
        os.makedirs(algorithm_path.parent)
        with open(algorithm_path, "w") as f:
            f.write("data")

        algorithm = mock.MagicMock()
        algorithm.path.path = str(algorithm_path)

        delete_algorithm_file(algorithm, algorithm)

        self.assertFalse(os.path.isfile(algorithm_path))
        self.assertFalse(os.path.isdir(algorithm_path.parent))
        self.assertTrue(os.path.isdir(settings.ALGORITHM_ROOT_DIR))

    def test_execution_delete_signal(self):
        execution_zip_path = settings.EXPERIMENT_ROOT_DIR / "test_dir" / "result.zip"
        os.makedirs(execution_zip_path.parent)
        with open(execution_zip_path, "w") as f:
            f.write("data")

        execution = mock.MagicMock()
        execution.pk = 3
        execution.is_running = False
        execution.result_path.path = str(execution_zip_path)

        delete_result_file(execution, execution)

        self.assertFalse(os.path.isfile(execution_zip_path))
        self.assertFalse(os.path.isdir(execution_zip_path.parent))
        self.assertTrue(os.path.isdir(settings.EXPERIMENT_ROOT_DIR))

    def test_execution_delete_running_execution(self):
        execution = mock.MagicMock()
        execution.pk = 3
        execution.is_running = True
        execution.result_path = None
        execution.experiment.pk = 12
        execution.experiment.user.pk = 99

        execution_running_dir = Path(get_result_path(execution))
        os.makedirs(execution_running_dir)
        with open(execution_running_dir / "file1", "w") as f:
            f.write("data in first result")
        with open(execution_running_dir / "file2", "w") as f:
            f.write("data in second result")

        assert os.path.isfile(execution_running_dir / "file1")
        assert os.path.isfile(execution_running_dir / "file2")

        delete_result_file(execution, execution)

        self.assertFalse(os.path.isdir(execution_running_dir))
        self.assertTrue(os.path.isdir(execution_running_dir.parent))

