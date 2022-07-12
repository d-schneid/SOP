import unittest
from unittest.mock import MagicMock, Mock

from backend.task.execution.core.Execution import Execution as e
from backend.task.execution.core.ExecutionElement import ExecutionElement as ee
from backend.task.execution.core.ExecutionSubspace import ExecutionSubspace as es
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm


class ExecutionElement(unittest.TestCase):

    _user_id: int = 414
    _task_id: int = 42
    _priority: int = 9999

    _es: es = MagicMock()
    _es.user_id = Mock(return_value=_user_id)
    _es.task_id = Mock(return_value=_task_id)
    _es.priority = Mock(return_value=_priority)

    _algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("algorithm_path", {}, "display_name")
    _result_path: str = "ee_result_path"
    _ee: ee = ee(_es, _algorithm, _result_path)

    def test_getter(self):
        self.assertEqual(self._ee.user_id, self._es.user_id)
        self.assertEqual(self._ee.task_id, self._es.task_id)
        self.assertEqual(self._ee.priority, self._ee._priority)


if __name__ == '__main__':
    unittest.main()
