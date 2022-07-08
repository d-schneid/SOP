import unittest
from unittest.mock import Mock

from backend_library.src.main.backend.task.execution.core.Execution import Execution as e
from backend_library.src.main.backend.task.execution.core.ExecutionElement import ExecutionElement as ee
from backend_library.src.main.backend.task.execution.core.ExecutionSubspace import ExecutionSubspace as es
from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm


class ExecutionElement(unittest.TestCase):

    def setUp(self) -> None:
        self._es: es = Mock()

        self._algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("algorithm_path", {}, "display_name")
        self._result_path: str = "ee_result_path"
        self._ee: ee = ee(self._es, self._algorithm, self._result_path)

    def test_getter(self):
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
