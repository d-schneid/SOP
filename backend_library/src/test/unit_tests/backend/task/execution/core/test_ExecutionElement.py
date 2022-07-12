import os
import unittest
import numpy as np
from unittest.mock import Mock

from backend.task.execution.core.ExecutionElement import ExecutionElement as ee
from backend.task.execution.core.ExecutionSubspace import ExecutionSubspace as es
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.DataIO import DataIO


class ExecutionElement(unittest.TestCase):

    _user_id: int = 414
    _task_id: int = 42
    _priority: int = 9999

    _es: es = Mock()
    _es.user_id = Mock(return_value=_user_id)
    _es.task_id = Mock(return_value=_task_id)
    _es.priority = Mock(return_value=_priority)

    _algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("algorithm_path", {}, "display_name")

    _dir_name: str = os.getcwd()
    _result_path: str = os.path.join(_dir_name, "ee_result_path.csv")
    _ee: ee = ee(_es, _algorithm, _result_path)

    def test_getter(self):
        self.assertEqual(self._ee.user_id, self._es.user_id)
        self.assertEqual(self._ee.task_id, self._es.task_id)
        self.assertEqual(self._ee.priority, self._ee._priority)

    def test_finished_result_exists(self):
        self.assertFalse(self._ee.finished_result_exists())
        DataIO.write_csv(self._result_path, np.asarray([["I am the execution element result"]]))
        self.assertTrue(self._ee.finished_result_exists())
        os.remove(self._result_path)
        self.assertFalse(self._ee.finished_result_exists())


if __name__ == '__main__':
    unittest.main()
