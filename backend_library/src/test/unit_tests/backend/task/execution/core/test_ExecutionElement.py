import os
import unittest
import numpy as np
from unittest.mock import Mock

from backend.task.TaskHelper import TaskHelper
from backend.task.execution.core.ExecutionElement import ExecutionElement as ee
from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.DataIO import DataIO
from multiprocessing.shared_memory import SharedMemory


class UnitTestExecutionElement(unittest.TestCase):
    # parameters for Execution Subspace/Element
    _user_id: int = 414
    _task_id: int = 42
    _priority: int = 10

    # create Execution Element
    _datapoint_count: int = 1

    _dir_name: str = os.getcwd()
    _result_path: str = "./test/unit_tests/backend/task/" \
                        "execution/core/execution_element_unit_test_result.csv"

    _row_numbers = np.array([0])

    _subspace: Subspace = Subspace(np.asarray([True, True, True]))
    _algorithm: ParameterizedAlgorithm = ParameterizedAlgorithm("algorithm_path", {},
                                                                "display_name")

    _subspace_dtype: np.dtype = np.dtype('f4')
    _subspace_shared_memory_name: str = "Subspace Shared Memory Name"

    def setUp(self) -> None:
        self._ee: ee = ee(self._user_id, self._task_id, self._subspace, self._algorithm,
                          self._result_path,
                          self._subspace_dtype, self._subspace_shared_memory_name,
                          self.__execution_element_is_finished1, self._datapoint_count,
                          self._row_numbers,
                          self._priority)

        # mock Execution Element for do_work()
        self._ee._ExecutionElement__run_algorithm = Mock(
            return_value=np.asarray([["algorithm result"]]))
        self._ee._ExecutionElement__convert_result_to_csv = Mock(
            return_value=np.asarray([["converted algorithm result"]]))
        self._ee1_is_finished: bool = False

    def tearDown(self) -> None:
        if os.path.isfile(self._result_path):
            os.remove(self._result_path)

    def __get_subspace_data_for_processing_callback(self) -> SharedMemory:
        pass

    def __execution_element_is_finished1(self, error_occurred: bool,
                                         aborted: bool = False) -> None:
        self._ee1_is_finished = True

    def __execution_element_is_finished(self, error_occurred: bool) -> None:
        pass

    def test_dont_create_execution_element_with_wrong_user_id_or_task_id(self):
        _wrong_user_id: int = -2
        _wrong_task_id: int = -2

        with self.assertRaises(AssertionError):
            self._ee_wrong_user_id: ee = ee(_wrong_user_id, self._task_id,
                                            self._subspace,
                                            self._algorithm, self._result_path,
                                            self._subspace_dtype, "",
                                            self.__execution_element_is_finished,
                                            self._datapoint_count, self._row_numbers)

        with self.assertRaises(AssertionError):
            self._ee_wrong_task_id: ee = ee(self._user_id, _wrong_task_id,
                                            self._subspace,
                                            self._algorithm, self._result_path,
                                            self._subspace_dtype, "",
                                            self.__execution_element_is_finished,
                                            self._datapoint_count, self._row_numbers)

    def test_properties(self):
        self.assertEqual(self._ee.user_id, self._user_id)
        self.assertEqual(self._ee.task_id, self._task_id)
        self.assertEqual(self._ee.priority, self._priority)

    def test_finished_result_exists(self):
        self.assertFalse(self._ee.finished_result_exists())
        DataIO.write_csv(self._result_path,
                         np.asarray([["I am the execution element result"]]))
        self.assertTrue(self._ee.finished_result_exists())
        os.remove(self._result_path)
        self.assertFalse(self._ee.finished_result_exists())

    def test_do_work_failed(self):
        error_file_path: str = TaskHelper.convert_to_error_csv_path(self._result_path)
        if os.path.isfile(error_file_path):
            os.remove(error_file_path)

        self._ee_faulty: ee = ee(self._user_id, self._task_id, self._subspace,
                                 self._algorithm,
                                 self._result_path,
                                 self._subspace_dtype,
                                 self._subspace_shared_memory_name,
                                 self.__execution_element_is_finished1,
                                 self._datapoint_count, self._row_numbers)

        # mock Execution Element for do_work()
        error_message_to_display: str = "ERROR I am going to throw an evil exception"
        self._ee._ExecutionElement__run_algorithm = Mock(
                        side_effect=Exception(error_message_to_display))

        # Method that should be tested
        statuscode = self._ee.do_work()

        # Test the results
        self.assertEqual(-1, statuscode)
        self.assertTrue(os.path.isfile(error_file_path))
        written_error_message: np.ndarray = \
            DataIO.read_uncleaned_csv(error_file_path, None)

        np.testing.assert_array_equal(written_error_message,
                                      np.asarray([[error_message_to_display]]))

        # clean up
        self._ee.run_later_on_main(statuscode)

        self.assertFalse(os.path.isfile(self._result_path))
        self.assertFalse(self._ee.finished_result_exists())

    def test_do_work_failed_with_empty_error_message(self):
        error_file_path: str = TaskHelper.convert_to_error_csv_path(
            self._result_path)
        if os.path.isfile(error_file_path):
            os.remove(error_file_path)

        self._ee_faulty: ee = ee(self._user_id, self._task_id, self._subspace,
                                 self._algorithm,
                                 self._result_path,
                                 self._subspace_dtype,
                                 self._subspace_shared_memory_name,
                                 self.__execution_element_is_finished1,
                                 self._datapoint_count, self._row_numbers)

        # mock Execution Element for do_work()
        error_message_to_display: str = ""
        self._ee._ExecutionElement__run_algorithm = Mock(
                        side_effect=Exception(error_message_to_display))

        # Method that should be tested
        statuscode = self._ee.do_work()

        # Test the results
        self.assertEqual(-1, statuscode)
        self.assertTrue(os.path.isfile(error_file_path))
        written_error_message: np.ndarray = \
            DataIO.read_uncleaned_csv(error_file_path, None)

        automatic_error_message: str = \
            "Error occurred while processing the ExecutionElement"
        np.testing.assert_array_equal(written_error_message,
                                      np.asarray([[automatic_error_message]]))

        # clean up
        self._ee.run_later_on_main(statuscode)

        self.assertFalse(os.path.isfile(self._result_path))
        self.assertFalse(self._ee.finished_result_exists())

    def test_wrong_priority(self):
        self._wrong_priority: list[int] = list([0, 4, -1, 9, -12313, 12431, 101, 102])
        for wrong_priority in self._wrong_priority:
            with self.assertRaises(AssertionError):
                ee(self._user_id, self._task_id, self._subspace, self._algorithm,
                   self._result_path,
                   self._subspace_dtype, self._subspace_shared_memory_name,
                   self.__execution_element_is_finished1, 1, self._row_numbers,
                   wrong_priority)


if __name__ == '__main__':
    unittest.main()
