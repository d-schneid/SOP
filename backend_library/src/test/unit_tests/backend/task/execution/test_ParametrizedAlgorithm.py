import json
import unittest

from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm


class UnitTestParameterizedAlgorithm(unittest.TestCase):
    _hyper_parameter: dict = []
    _display_name: str = "display_name"

    _parameterized_algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("path", _hyper_parameter,
                                                                              _display_name)

    def test_parameterized_algorithm_getter(self):
        self.assertEqual(self._parameterized_algorithm.display_name, self._display_name)
        self.assertEqual(self._parameterized_algorithm.hyper_parameter, self._hyper_parameter)
        self.assertEqual(self._parameterized_algorithm.directory_name_in_execution, "")

    def test_directory_name_in_execution(self):
        parameterized_algorithm2: ParameterizedAlgorithm = ParameterizedAlgorithm("path", self._hyper_parameter,
                                                                                  self._display_name)
        self.assertEqual(parameterized_algorithm2.directory_name_in_execution, "")
        parameterized_algorithm2.directory_name_in_execution = "new_directory_name"
        self.assertEqual(parameterized_algorithm2.directory_name_in_execution, "new_directory_name")

    def test_to_json(self):
        json_str = '{"display_name": "display_name",' \
                   ' "directory_name": "", "hyper_parameter": []}'
        self.assertEqual(json_str, json.dumps(self._parameterized_algorithm.to_json()))


if __name__ == '__main__':
    unittest.main()
