import json
from unittest.mock import MagicMock, patch

import django.test
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.urls import reverse_lazy

from experiments.models import Execution
from experiments.models.execution import ExecutionStatus
from experiments.views.execution import (
    download_execution_result,
    get_execution_progress,
)


class ExecutionViewTests(django.test.TestCase):
    def test_download_execution_result(self) -> None:
        content = "Line 1\nLine 2\nLast Line"
        request = MagicMock()
        request.method = "GET"
        objects_mock = MagicMock()
        objects_mock.filter.return_value.first.return_value.result_path.__enter__.return_value.read.return_value = (
            content
        )
        with patch.object(Execution, "objects", objects_mock):
            response = download_execution_result(request, 0, 1)
            self.assertIsNotNone(response)
            assert isinstance(response, HttpResponse)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, bytes(content, "utf-8"))
            self.assertEqual(
                response["Content-Disposition"], "attachment; filename=result.zip"
            )

    def test_download_execution_result_invalid_pk(self) -> None:
        request = MagicMock()
        request.method = "GET"
        objects_mock = MagicMock()
        objects_mock.filter.return_value.first.return_value = None
        with patch.object(Execution, "objects", objects_mock):
            response = download_execution_result(request, 0, 1)
            self.assertIsNotNone(response)
            assert isinstance(response, HttpResponseRedirect)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse_lazy("experiment_overview"))

    def test_download_execution_result_post(self) -> None:
        content = "Line 1\nLine 2\nLast Line"
        request = MagicMock()
        request.method = "POST"
        objects_mock = MagicMock()
        objects_mock.filter.return_value.first.return_value.result_path.__enter__.return_value.read.return_value = (
            content
        )
        with patch.object(Execution, "objects", objects_mock):
            response = download_execution_result(request, 0, 1)
            self.assertIsNone(response)

    def test_get_execution_progress(self) -> None:
        request = MagicMock()
        request.GET = {"execution_pk": 3}
        execution = MagicMock()
        execution.progress = 0.314
        execution.status = ExecutionStatus.RUNNING.name
        execution.pk = 3
        objects_mock = MagicMock()
        objects_mock.filter.return_value.first.return_value = execution
        with patch.object(Execution, "objects", objects_mock):
            response = get_execution_progress(request)
            dikt = json.loads(response.content)
            self.assertDictEqual(
                dikt,
                {
                    "progress": execution.progress,
                    "status": execution.status,
                    "execution_pk": execution.pk,
                },
            )

    def test_get_execution_progress_invalid_pk(self) -> None:
        request = MagicMock()
        request.GET = {"execution_pk": 3}
        response = get_execution_progress(request)
        dikt = json.loads(response.content)
        self.assertDictEqual(dikt, {})

    def test_get_execution_progress_no_pk_given(self) -> None:
        request = MagicMock()
        response = get_execution_progress(request)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(isinstance(response, HttpResponseServerError))
