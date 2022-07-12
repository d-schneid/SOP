import os
import unittest
from unittest import mock, skip

import ddt as ddt
import numpy as np
from unittest.mock import Mock, PropertyMock, patch

from backend.task.execution.core.Execution import Execution
from backend.task.execution.core.ExecutionElement import ExecutionElement as ee
from backend.task.execution.core.ExecutionSubspace import ExecutionSubspace as es
from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.DataIO import DataIO


class UnitTestExecutionElement(unittest.TestCase):
    # TODO: Maybe remove mocking through using non cyclic dependencies in execution-core
    # parameters for Execution Subspace/Element
    _user_id: int = 414
    _task_id: int = 42
    _priority: int = 9999

    # mock Execution Subspace
    _es: es = Mock()
    _es._user_id = Mock(return_value=_user_id)
    _es._task_id = Mock(return_value=_task_id)

    # create Execution Element
    _dir_name: str = os.getcwd()
    _result_path: str = os.path.join(_dir_name, "ee_result_path.csv")

    _algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("algorithm_path", {}, "display_name")

    _ee: ee = ee(_es, _algorithm, _result_path)

    # mock Execution Element for do_work()
    _ee._ExecutionElement__run_algorithm = Mock(return_value=np.asarray([["algorithm result"]]))
    _ee._ExecutionElement__convert_result_to_csv = Mock(return_value=np.asarray([["converted algorithm result"]]))

    def tearDown(self) -> None:
        if os.path.isfile(self._result_path):
            os.remove(self._result_path)

    @skip
    def test_getter(self):
        # TODO: user_id und task_id sind noch falsch gemocked!!!
        print("TEST")
        print(self._es._execution._user_id)
        print(self._ee._user_id)
        print(self._es.user_id)
        print(self._ee.priority)
        self.assertEqual(self._ee.user_id, self._user_id)
        self.assertEqual(self._ee.task_id, self._task_id)
        self.assertEqual(self._ee.priority, self._priority)

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
