import os
import shutil
import unittest
from unittest.mock import Mock

import numpy as np

from backend.scheduler.Scheduler import Scheduler
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core.ExecutionElement import ExecutionElement
from backend.task.execution.core.ExecutionSubspace import ExecutionSubspace
from backend.task.execution.subspace.Subspace import Subspace
from test.DebugScheduler2 import DebugScheduler2


class UnitTestExecutionSubspace(unittest.TestCase):
    # parameters for Execution
    _user_id: int = 21412
    _task_id: int = 424242
    _priority: int = 5

    _datapoint_count: int = 1

    _subspace: Subspace = Subspace(np.asarray([True, False, True, True, True]))
    _ds: np.ndarray = np.ndarray((1, 5), dtype=np.dtype('f4'))
    _row_numbers = np.array([0, 1, 2, 3])
    # parameterized algorithms
    _hyper_parameter: dict = {"seed": 0}
    _display_names: list[str] = [
        "display_name",
        "display_name",
        "different_display_name",
        "display_name",
    ]
    _directory_names_in_execution: list[str] = [
        "display_name",
        "display_name (1)",
        "different_display_name",
        "display_name (2)",
    ]

    _algorithms: list[ParameterizedAlgorithm] = list(
        [
            ParameterizedAlgorithm("path", _hyper_parameter, _display_names[0]),
            ParameterizedAlgorithm("path2", _hyper_parameter, _display_names[1]),
            ParameterizedAlgorithm("path3", _hyper_parameter, _display_names[2]),
            ParameterizedAlgorithm("path3", _hyper_parameter, _display_names[3]),
        ]
    )

    _dir_name: str = os.getcwd()
    _result_path: str = os.path.join(_dir_name, "execution_folder")

    _subspace_dtype: np.dtype = np.dtype("f4")

    Scheduler._instance = None
    _debug_scheduler: DebugScheduler2 = DebugScheduler2()

    _ds_shm_name: str = "Shared Memory Name"

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        self._debug_scheduler: DebugScheduler2 = DebugScheduler2()

        # Execution Logic
        self._execution_elements_finished1: int = 0
        # create ExecutionSubspace
        self._es: ExecutionSubspace = ExecutionSubspace(
            self._user_id, self._task_id,
            self._algorithms,
            self._subspace,
            self._result_path,
            self._ds,
            self.__on_execution_element_finished1,
            self._ds_shm_name, self._row_numbers
        )
        self._es.run_later_on_main(0)

    def tearDown(self) -> None:
        self.__clear_old_execution_file_structure()

    def __on_execution_element_finished(self, error: bool) -> None:
        pass

    def __on_execution_element_finished1(self, error: bool, aborted: bool = False) \
            -> None:
        self._execution_elements_finished1 += 1

    def test_dont_create_execution_element_with_wrong_user_id_or_task_id(self):
        _wrong_user_id: int = -2
        _wrong_task_id: int = -2

        with self.assertRaises(AssertionError):
            self._es_wrong_user_id: ExecutionSubspace = ExecutionSubspace(
                _wrong_user_id,
                self._task_id,
                self._algorithms,
                self._subspace,
                self._result_path,
                self._ds,
                self.__on_execution_element_finished,
                self._ds_shm_name, self._row_numbers
            )

        with self.assertRaises(AssertionError):
            self._es_wrong_task_id: ExecutionSubspace = ExecutionSubspace(
                self._user_id,
                _wrong_task_id,
                self._algorithms,
                self._subspace,
                self._result_path,
                self._ds,
                self.__on_execution_element_finished,
                "", self._row_numbers
            )

    def test_getter(self):
        self.assertEqual(self._user_id, self._es.user_id)
        self.assertEqual(self._task_id, self._es.task_id)
        self.assertEqual(self._priority, self._es.priority)

    def test_generate_execution_elements(self):
        # The method will be called on creation of ExecutionSubspace (in constructor
        # -> just test outcome)
        self.assertEqual(len(self._algorithms), len(self._es._execution_elements))
        _execution_elements: list[ExecutionElement] = list(self._es._execution_elements)
        _algorithms_count_in_execution_elements: int = 0
        for algorithm in self._algorithms:
            for execution_element in _execution_elements:
                if execution_element._algorithm == algorithm:
                    _algorithms_count_in_execution_elements += 1
                    break

        # Every algorithm has to be in one ExecutionElement:
        self.assertEqual(_algorithms_count_in_execution_elements, len(self._algorithms))

    def test_schedule_execution_elements(self):
        # (create a new Execution in the actual test
        # so that the lines are seen as covered)

        # Setup
        Scheduler._instance = None
        self._debug_scheduler: DebugScheduler2 = DebugScheduler2()

        self.__clear_old_execution_file_structure()
        self._es: ExecutionSubspace = ExecutionSubspace(
            self._user_id, self._task_id,
            self._algorithms,
            self._subspace,
            self._result_path,
            self._ds,
            self.__on_execution_element_finished1,
            self._ds_shm_name, self._row_numbers
        )
        self._es.run_later_on_main(0)

        # Test if right amount of execution elements are created
        self.assertEqual(
            self._debug_scheduler.called_scheduler_amount, len(self._algorithms)
        )

    def test_execution_element_is_finished(self):
        self._es._ExecutionSubspace__unload_subspace_shared_memory = \
            Mock(return_value=None)

        # normal logic -> count up _finished_execution_element_count
        for element in range(0, self._es._total_execution_element_count):
            self.assertEqual(self._es._finished_execution_element_count, element)
            self._es._ExecutionSubspace__execution_element_is_finished(False)
        self.assertEqual(self._es._finished_execution_element_count,
                         self._es._total_execution_element_count)

        # out of range (more elements finished than elements exists)
        with self.assertRaises(AssertionError):
            self._es._ExecutionSubspace__execution_element_is_finished(False)

        self.assertEqual(self._es._finished_execution_element_count,
                         self._es._total_execution_element_count)

    def __clear_old_execution_file_structure(self):

        if os.path.isdir(self._result_path):
            shutil.rmtree(self._result_path)

    def test_wrong_priority(self):
        self._wrong_priority: list[int] = list([0, 4, -1, 10, -12313, 12431])
        for wrong_priority in self._wrong_priority:
            with self.assertRaises(AssertionError):
                self._es: ExecutionSubspace = ExecutionSubspace(
                    self._user_id, self._task_id,
                    self._algorithms,
                    self._subspace,
                    self._result_path,
                    self._ds,
                    self.__on_execution_element_finished1,
                    self._ds_shm_name, self._row_numbers,
                    wrong_priority
                )


if __name__ == "__main__":
    unittest.main()
