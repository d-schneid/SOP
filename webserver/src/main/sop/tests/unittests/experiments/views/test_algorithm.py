from unittest import mock
from unittest.mock import MagicMock

import django.test
from django.urls import reverse_lazy

from experiments.models import Algorithm
from experiments.views.algorithm import download_algorithm


class DatasetViewTests(django.test.TestCase):
    def test_download_algorithm(self) -> None:
        content = "Line 1\nLine 2\nLast Line"
        algorithm = MagicMock()
        algorithm.display_name = "algorithm_name"
        algorithm.pk = 3
        algorithm.path.__enter__.return_value.read.return_value = content
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = algorithm
        request = MagicMock()
        request.method = "GET"
        with mock.patch.object(Algorithm, "objects", object_mock):
            response = download_algorithm(request, algorithm.pk)
            self.assertIsNotNone(response)
            assert response is not None
            self.assertEqual(response.content, bytes(content, "utf-8"))
            self.assertEqual(
                response["Content-Disposition"],
                f"attachment; filename={algorithm.display_name}.py",
            )

    def test_download_algorithm_invalid_pk(self) -> None:
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = None
        request = MagicMock()
        request.method = "GET"
        with mock.patch.object(Algorithm, "objects", object_mock):
            response = download_algorithm(request, 42)
            self.assertIsNotNone(response)
            assert response is not None
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse_lazy("algorithm_overview"))  # type: ignore

    def test_download_algorithm_post(self) -> None:
        object_mock = MagicMock()
        object_mock.filter.return_value.first.return_value = None
        request = MagicMock()
        request.method = "POST"
        with mock.patch.object(Algorithm, "objects", object_mock):
            response = download_algorithm(request, 42)
            self.assertIsNone(response)
