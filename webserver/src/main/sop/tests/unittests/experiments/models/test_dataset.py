import os.path
from unittest.mock import MagicMock, patch

import django.test

from experiments.models import Experiment
from experiments.models.dataset import get_dataset_upload_path, Dataset


class DatasetModelTests(django.test.TestCase):
    def test_get_dataset_upload_path(self) -> None:
        dataset = MagicMock()
        dataset.user.id = 3
        filename = "dataset.csv"
        path = get_dataset_upload_path(dataset, filename)
        self.assertEqual(
            path,
            os.path.join("datasets", f"user_{dataset.user.id}", filename),
        )

    def test_is_deletable(self) -> None:
        experiment_objects_mock = MagicMock()
        queryset_mock = MagicMock()
        queryset_mock.exists.return_value = True
        experiment_objects_mock.get_with_dataset.return_value = queryset_mock
        dataset = Dataset()
        with patch.object(Experiment, "objects", experiment_objects_mock):
            self.assertFalse(dataset.is_deletable)

    def test_is_deletable_false(self) -> None:
        experiment_objects_mock = MagicMock()
        queryset_mock = MagicMock()
        queryset_mock.exists.return_value = False
        experiment_objects_mock.get_with_dataset.return_value = queryset_mock
        dataset = Dataset()
        with patch.object(Experiment, "objects", experiment_objects_mock):
            self.assertTrue(dataset.is_deletable)
