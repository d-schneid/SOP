import json
import unittest

from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm


class ParameterizedAlgorithmTests(unittest.TestCase):
    hyper_parameter: dict = []
    display_name: str = "display_name"

    def setUp(self) -> None:
        self._parameterized_algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("path", self.hyper_parameter,
                                                                                       self.display_name)

    def tearDown(self) -> None:
        self._parameterized_algorithm = None

    def test_parameterized_algorithm_getter(self):
        self.assertEqual(self._parameterized_algorithm.display_name, self.display_name)
        self.assertEqual(self._parameterized_algorithm.hyper_parameter, self.hyper_parameter)
        self.assertEqual(self._parameterized_algorithm.directory_name_in_execution, "")

    def test_directory_name_in_execution(self):
        parameterized_algorithm2: ParameterizedAlgorithm = ParameterizedAlgorithm("path", self.hyper_parameter,
                                                                                       self.display_name)
        self.assertEqual(parameterized_algorithm2.directory_name_in_execution, "")
        parameterized_algorithm2.directory_name_in_execution = "new_directory_name"
        self.assertEqual(parameterized_algorithm2.directory_name_in_execution, "new_directory_name")

    def test_to_json(self):
        to_json_dict = {'display_name': self.display_name, 'directory_name': "",
                        'hyper_parameter': self.hyper_parameter}
        json_str = json.dumps(to_json_dict, indent=4)
        self.assertEqual(json_str, self._parameterized_algorithm.to_json())


if __name__ == '__main__':
    unittest.main()
