from unittest.mock import MagicMock, patch

import django.test
from django.http.response import HttpResponse

from experiments.models import Experiment, Execution
from experiments.views.experiment import download_all_execution_results


class ExperimentDownloadResultsTest(django.test.TestCase):
    def execution_mock(self, result_text: str, id: int) -> MagicMock:
        mock = MagicMock()
        mock.has_result = True
        mock.result_path.__enter__.return_value.read.return_value = result_text
        mock.result_path.__enter__.return_value.path = f"/test/path/to/result_{id}.zip"
        return mock

    def test_download_all_results(self):
        content1 = "Line 1\nLine 2\nLast Line"
        content2 = "Results of second execution"
        content3 = "Last result text"
        request = MagicMock()
        request.method = "GET"

        experiment = MagicMock()
        experiment.display_name = "Nice Experiment"

        exp_objects_mock = MagicMock()
        exp_objects_mock.filter.return_value.exists.return_value = True
        exp_objects_mock.get.return_value = experiment

        execution1 = self.execution_mock(content1, 1)
        execution2 = self.execution_mock(content2, 2)
        execution3 = self.execution_mock(content3, 3)
        executions = [execution1, execution2, execution3]

        exec_objects_mock = MagicMock()
        exec_objects_mock.filter.return_value = executions

        with patch.object(Experiment, "objects", exp_objects_mock):
            with patch.object(Execution, "objects", exec_objects_mock):
                response = download_all_execution_results(request, 3)
                self.assertIsNotNone(response)
                self.assertIsInstance(response, HttpResponse)
                self.assertEqual(response.status_code, 200)
                self.assertNotEqual(
                    str(response.content).find(content1.replace("\n", "\\n")), -1
                )
                self.assertNotEqual(str(response.content).find(content2), -1)
                self.assertNotEqual(str(response.content).find(content3), -1)

                self.assertEqual(
                    response["Content-Disposition"],
                    f"attachment; filename={experiment.display_name}_results.zip",
                )
