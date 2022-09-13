import unittest
from unittest.mock import MagicMock, patch

import django.test

from backend.task.execution.core.Execution import Execution as BackendExecution
from experiments.services.execution import get_params_out_of_form, schedule_backend


class ExecutionServiceTests(django.test.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.algo1 = MagicMock()
        self.algo1.pk = 4
        self.algo1.get_signature_as_dict.return_value = {
            "param1": "Cool String",
            "param2": 42,
            "param3": 3.14,
            "param4": [1, 2, "abc"],
            "param5": None,
        }
        self.algo2 = MagicMock()
        self.algo2.pk = 8
        self.algo2.get_signature_as_dict.return_value = {
            "param1": "Another String",
            "param2": 69,
            "param3": 5.8,
            "param4": [4.2, "hello"],
            "param5": None,
        }
        self.experiment = MagicMock()
        self.experiment.algorithms.all.return_value = [self.algo1, self.algo2]

        self.request = MagicMock()
        self.request.POST = {
            "4_param1": "'Replacement String'",
            "4_param2": "21",
            "4_param3": "6.9",
            "4_param4": "[x**2 for x in range(10)]",
            "4_param5": "None",
            "8_param1": '"Look, another one"',
            "8_param2": "42",
            "8_param3": "7.2",
            "8_param4": '["Hello", "World"]',
            "8_param5": "None",
        }

        self.result = {
            "4": {
                "param1": "Replacement String",
                "param2": 21,
                "param3": 6.9,
                "param4": [0, 1, 4, 9, 16, 25, 36, 49, 64, 81],
                "param5": None,
            },
            "8": {
                "param1": "Look, another one",
                "param2": 42,
                "param3": 7.2,
                "param4": ["Hello", "World"],
                "param5": None,
            },
        }

    def test_get_params_out_of_form_valid(self) -> None:
        success, return_dict = get_params_out_of_form(self.request, self.experiment)
        self.assertTrue(success)
        self.assertDictEqual(self.result, return_dict)

    def test_get_params_out_of_form_invalid(self) -> None:
        self.request.POST["4_param1"] = "world"
        self.request.POST["8_param3"] = "hello"
        success, return_dict = get_params_out_of_form(self.request, self.experiment)
        self.assertFalse(success)
        self.assertEqual(len(return_dict.keys()), 2)
        self.assertListEqual(
            return_dict.get("4_param1"), ["strings must be wrapped in quotes"]
        )
        self.assertListEqual(
            return_dict.get("8_param3"), ["strings must be wrapped in quotes"]
        )

    def test_get_params_out_of_form_invalid_syntax(self) -> None:
        self.request.POST["8_param1"] = "'key': 'value'}"
        self.request.POST["8_param4"] = "['hello', 3, 'World'"
        success, return_dict = get_params_out_of_form(self.request, self.experiment)
        self.assertFalse(success)
        self.assertEqual(len(return_dict.keys()), 2)
        self.assertIsNotNone(return_dict.get("8_param4"))
        self.assertIsNotNone(return_dict.get("8_param1"))

    def test_schedule_backend(self) -> None:
        algo1 = MagicMock()
        algo1.path.path = "algorithm/path"
        algo1.display_name = "Algo 1"
        algo1.pk = 69
        algo2 = MagicMock()
        algo2.path.path = "algorithm/path/2"
        algo2.display_name = "Algo 2"
        algo2.pk = 42
        execution = MagicMock()
        execution.pk = 12
        execution.subspaces_min = 2
        execution.subspaces_max = 5
        execution.subspace_amount = 3
        execution.subspace_generation_seed = 123456789
        execution.get_result_path.return_value = "another/cool/path"
        execution.algorithm_parameters = {
            f"{algo1.pk}": {"param1": 8, "param2": "World"},
            f"{algo2.pk}": {"param1": 3.14, "param2": "was None"},
        }

        execution.experiment.dataset.dimensions_total = 20
        execution.experiment.dataset.path_cleaned.path = (
            "cool/path/to/dataset_cleaned.csv"
        )
        execution.experiment.dataset.datapoints_total = 200

        execution.experiment.user.pk = 3
        execution.experiment.algorithms.all.return_value = [algo1, algo2]

        with patch.object(BackendExecution, "schedule", lambda s: None):
            errors = schedule_backend(execution)
            self.assertIsNone(errors)

    def test_schedule_backend_not_enough_subspaces(self) -> None:
        execution = MagicMock()
        execution.pk = 12
        execution.subspaces_min = 2
        execution.subspaces_max = 5
        execution.subspace_amount = 1000

        execution.experiment.dataset.dimensions_total = 20
        execution.experiment.algorithms.all.return_value = []

        with patch.object(BackendExecution, "schedule", lambda s: None):
            errors = schedule_backend(execution)
            assert errors is not None
            self.assertEqual(len(errors.keys()), 1)
            self.assertIsNotNone(errors.get("subspace_amount"))


if __name__ == "__main__":
    unittest.main()
