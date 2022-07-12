import os
import unittest
from unittest import mock

import numpy as np
from unittest.mock import Mock

from backend.task.execution.core.ExecutionElement import ExecutionElement as ee
from backend.task.execution.core.ExecutionSubspace import ExecutionSubspace as es
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.DataIO import DataIO


class TestExecutionElement(unittest.TestCase):

    # parameters for Execution Subspace/Element
    _user_id: int = 414
    _task_id: int = 42
    _priority: int = 9999

    # mock Execution Subspace
    _es: es = Mock()
    _es.user_id = Mock(return_value=_user_id)
    _es.task_id = Mock(return_value=_task_id)
    _es.priority = Mock(return_value=_priority)

    # create Execution Element
    _algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("algorithm_path", {}, "display_name")

    _dir_name: str = os.getcwd()
    _result_path: str = os.path.join(_dir_name, "ee_result_path.csv")
    _ee: ee = ee(_es, _algorithm, _result_path)

    # mock Execution Element for do_work()
    _ee._ExecutionElement__run_algorithm = Mock(return_value=np.asarray([["algorithm result"]]))
    _ee._ExecutionElement__convert_result_to_csv = Mock(return_value=np.asarray([["converted algorithm result"]]))

    def tearDown(self) -> None:
        if os.path.isfile(self._result_path):
            os.remove(self._result_path)

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

    def test_do_work(self):
        self.assertFalse(self._ee.finished_result_exists())

        # Method that should be tested
        self._ee.do_work()

        # Tests if do_work saved the converted algorithm result
        self.assertTrue(self._ee.finished_result_exists())
        self.assertEqual(DataIO.read_uncleaned_csv(self._result_path)[0, 0], "converted algorithm result")

        # clean up
        os.remove(self._result_path)
        self.assertFalse(self._ee.finished_result_exists())


if __name__ == '__main__':
    unittest.main()
