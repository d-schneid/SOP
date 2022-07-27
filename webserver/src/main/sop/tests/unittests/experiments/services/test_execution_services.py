import unittest
from unittest.mock import MagicMock

from django.test import TestCase

from experiments.services.execution import get_params_out_of_form


class ExecutionServiceTests(TestCase):
    def setUp(self) -> None:
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
        self.assertTrue(len(return_dict.keys()) == 2)
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
        self.assertTrue(len(return_dict.keys()) == 2)
        self.assertIsNotNone(return_dict.get("8_param4"))
        self.assertIsNotNone(return_dict.get("8_param1"))


if __name__ == "__main__":
    unittest.main()
