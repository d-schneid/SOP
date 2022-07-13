import os
import unittest
import numpy as np
from unittest.mock import Mock

from backend.task.execution.core.ExecutionElement import ExecutionElement as ee
from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.DataIO import DataIO
from multiprocessing.shared_memory import SharedMemory


class UnitTestExecutionElement(unittest.TestCase):
    # parameters for Execution Subspace/Element
    _user_id: int = 414
    _task_id: int = 42
    _priority: int = 9999

    # create Execution Element
    _dir_name: str = os.getcwd()
    _result_path: str = os.path.join(_dir_name, "ee_result_path.csv")

    _subspace: Subspace = Subspace(np.asarray([1, 1, 1]))
    _algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("algorithm_path", {}, "display_name")

    _subspace_dtype: np.dtype = np.dtype('f4')

    def setUp(self) -> None:
        self._ee: ee = ee(self._user_id, self._task_id, self._subspace, self._algorithm, self._result_path,
                          self._subspace_dtype, self.__get_subspace_data_for_processing_callback,
                          self.__execution_element_is_finished1, self._priority)

        # mock Execution Element for do_work()
        self._ee._ExecutionElement__run_algorithm = Mock(return_value=np.asarray([["algorithm result"]]))
        self._ee._ExecutionElement__convert_result_to_csv = Mock(
            return_value=np.asarray([["converted algorithm result"]]))
        self._ee1_is_finished: bool = False

    def tearDown(self) -> None:
        if os.path.isfile(self._result_path):
            os.remove(self._result_path)
        _ee = None

    def __get_subspace_data_for_processing_callback(self) -> SharedMemory:
        pass

    def __execution_element_is_finished1(self, error_occurred: bool) -> None:
        self._ee1_is_finished = True

    def __execution_element_is_finished(self, error_occurred: bool) -> None:
        pass

    def test_dont_create_execution_element_with_wrong_user_id_or_task_id(self):
        _wrong_user_id: int = -2
        _wrong_task_id: int = -2

        with self.assertRaises(AssertionError) as context:
            self._ee_wrong_user_id: ee = ee(_wrong_user_id, self._task_id, self._subspace,
                                            self._algorithm, self._result_path,
                                            self._subspace_dtype, self.__get_subspace_data_for_processing_callback,
                                            self.__execution_element_is_finished,
                                            self._priority)

        with self.assertRaises(AssertionError) as context:
            self._ee_wrong_task_id: ee = ee(self._user_id, _wrong_task_id, self._subspace,
                                            self._algorithm, self._result_path,
                                            self._subspace_dtype, self.__get_subspace_data_for_processing_callback,
                                            self.__execution_element_is_finished,
                                            self._priority)

    def test_getter(self):
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
        self.assertFalse(self._ee1_is_finished)

        # Method that should be tested
        self._ee.do_work()

        # Tests if do_work() saved the converted algorithm result
        self.assertTrue(self._ee.finished_result_exists())
        self.assertEqual(DataIO.read_uncleaned_csv(self._result_path)[0, 0], "converted algorithm result")

        # Test callback
        self.assertTrue(self._ee1_is_finished)

        # clean up
        os.remove(self._result_path)
        self.assertFalse(self._ee.finished_result_exists())


if __name__ == '__main__':
    unittest.main()
