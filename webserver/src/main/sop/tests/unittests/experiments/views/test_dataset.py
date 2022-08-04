from unittest import mock
from unittest.mock import MagicMock

import django.test
from django.urls import reverse_lazy

from experiments.models import Dataset
from experiments.services.dataset import get_download_response
from experiments.views.dataset import (
    download_uncleaned_dataset,
    download_cleaned_dataset,
)


class DatasetViewTests(django.test.TestCase):
    def test_get_download_response(self) -> None:
        file = MagicMock()
        content = "Line 1\nLine 2\nLast Line"
        file.read.return_value = content
        download_name = "file.txt"
        response = get_download_response(file, download_name)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertEqual(
            response["Content-Disposition"], f"attachment; filename={download_name}"
        )
        self.assertEqual(response.content, bytes(content, "utf-8"))

    def test_download_uncleaned_dataset(self) -> None:
        content = "Line 1\nLine 2\nLast Line"
        dataset = MagicMock()
        dataset.display_name = "dataset_name"
        dataset.pk = 3
        dataset.path_original.__enter__.return_value.read.return_value = content
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = dataset
        request = MagicMock()
        request.method = "GET"
        with mock.patch.object(Dataset, "objects", object_mock):
            response = download_uncleaned_dataset(request, dataset.pk)
            self.assertIsNotNone(response)
            assert response is not None
            self.assertEqual(response.content, bytes(content, "utf-8"))
            self.assertEqual(
                response["Content-Disposition"],
                f"attachment; filename={dataset.display_name}.csv",
            )

    def test_download_uncleaned_dataset_invalid_pk(self) -> None:
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = None
        request = MagicMock()
        request.method = "GET"
        with mock.patch.object(Dataset, "objects", object_mock):
            response = download_uncleaned_dataset(request, 42)
            self.assertIsNotNone(response)
            assert response is not None
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse_lazy("dataset_overview"))  # type: ignore

    def test_download_uncleaned_dataset_post(self) -> None:
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = None
        request = MagicMock()
        request.method = "POST"
        with mock.patch.object(Dataset, "objects", object_mock):
            response = download_uncleaned_dataset(request, 42)
            self.assertIsNone(response)

    def test_download_cleaned_dataset(self) -> None:
        content = "Line 1\nLine 2\nLast Line"
        dataset = MagicMock()
        dataset.display_name = "dataset_name"
        dataset.is_cleaned = True
        dataset.pk = 3
        dataset.path_cleaned.__enter__.return_value.read.return_value = content
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = dataset
        request = MagicMock()
        request.method = "GET"
        with mock.patch.object(Dataset, "objects", object_mock):
            response = download_cleaned_dataset(request, dataset.pk)
            self.assertIsNotNone(response)
            assert response is not None
            self.assertEqual(response.content, bytes(content, "utf-8"))
            self.assertEqual(
                response["Content-Disposition"],
                f"attachment; filename={dataset.display_name}_cleaned.csv",
            )

    def test_download_cleaned_dataset_invalid_pk(self) -> None:
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = None
        request = MagicMock()
        request.method = "GET"
        with mock.patch.object(Dataset, "objects", object_mock):
            response = download_cleaned_dataset(request, 42)
            self.assertIsNotNone(response)
            assert response is not None
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse_lazy("dataset_overview"))  # type: ignore

    def test_download_cleaned_dataset_not_cleaned(self) -> None:
        dataset = MagicMock()
        dataset.display_name = "dataset_name"
        dataset.is_cleaned = False
        dataset.pk = 3
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = dataset
        request = MagicMock()
        request.method = "GET"
        with mock.patch.object(Dataset, "objects", object_mock):
            response = download_cleaned_dataset(request, 42)
            self.assertIsNotNone(response)
            assert response is not None
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse_lazy("dataset_overview"))  # type: ignore

    def test_download_cleaned_dataset_post(self) -> None:
        dataset = MagicMock()
        dataset.display_name = "dataset_name"
        dataset.is_cleaned = False
        dataset.pk = 3
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = dataset
        request = MagicMock()
        request.method = "POST"
        with mock.patch.object(Dataset, "objects", object_mock):
            response = download_cleaned_dataset(request, 42)
            self.assertIsNone(response)
