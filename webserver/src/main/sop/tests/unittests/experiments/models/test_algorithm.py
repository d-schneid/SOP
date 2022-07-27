from unittest.mock import MagicMock

import django.test

from experiments.models.algorithm import get_algorithm_upload_path, Algorithm


class AlgorithmModelTests(django.test.TestCase):
    def test__get_algorithm_upload_path(self) -> None:
        algorithm = MagicMock()
        algorithm.user.pk = 3
        filename = "algo.py"
        path = get_algorithm_upload_path(algorithm, filename)
        self.assertEqual(path, f"algorithms/user_{algorithm.user.pk}/{filename}")

    def test__get_algorithm_upload_path_no_user(self) -> None:
        algorithm = MagicMock()
        algorithm.user = None
        filename = "algo.py"
        path = get_algorithm_upload_path(algorithm, filename)
        self.assertEqual(path, f"algorithms/user_0/{filename}")

    def test_get_signature_as_json(self) -> None:
        algorithm = Algorithm()
        params = {
            "param1": 3,
            "param2": "String",
            "param3": None,
            "param4": 3.14,
            "param5": ["Hello", "World"],
            "param6": {"key": "value"},
        }
        algorithm.signature = params
        dikt = algorithm.get_signature_as_dict()
        self.assertDictEqual(dikt, params)
