import os
import unittest
from multiprocessing.shared_memory import SharedMemory
from unittest.mock import Mock

import numpy as np

from backend.task.execution.core.ExecutionElement import ExecutionElement
from backend.task.execution.core.ExecutionSubspace import ExecutionSubspace
from backend.task.execution.core.Execution import Execution
from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.scheduler.DebugScheduler2 import DebugScheduler2
from backend.scheduler.Scheduler import Scheduler


class UnitTestExecutionSubspace(unittest.TestCase):
    # parameters for Execution
    _user_id: int = 21412
    _task_id: int = 424242

    _subspace: Subspace = Subspace(np.asarray([1, 0, 1, 1, 1]))

    # parameterized algorithms
    _hyper_parameter: dict = {'seed': 0}
    _display_names: list[str] = ["display_name", "display_name", "different_display_name", "display_name"]
    _directory_names_in_execution: list[str] = ["display_name", "display_name (1)", "different_display_name",
                                                "display_name (2)"]

    _algorithms: list[ParameterizedAlgorithm] = \
        list([ParameterizedAlgorithm("path", _hyper_parameter, _display_names[0]),
              ParameterizedAlgorithm("path2", _hyper_parameter, _display_names[1]),
              ParameterizedAlgorithm("path3", _hyper_parameter, _display_names[2]),
              ParameterizedAlgorithm("path3", _hyper_parameter, _display_names[3])])

    _dir_name: str = os.getcwd()
    _result_path: str = os.path.join(_dir_name, "execution_folder")

    _subspace_dtype: np.dtype = np.dtype('f4')

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        DebugScheduler2()


        # Execution Logic
        self._execution_elements_finished1: int = 0
        # create ExecutionSubspace
        self._es: ExecutionSubspace = ExecutionSubspace(self._user_id, self._task_id, self._algorithms, self._subspace,
                                                        self._result_path, self._subspace_dtype, self.__cache_dataset,
                                                        self.__on_execution_element_finished1)

    def __cache_dataset(self) -> SharedMemory:
        pass

    def __on_execution_element_finished(self, error: bool) -> None:
        pass

    def __on_execution_element_finished1(self, error: bool) -> None:
        self._execution_elements_finished1 += 1

    def test_dont_create_execution_element_with_wrong_user_id_or_task_id(self):
        _wrong_user_id: int = -2
        _wrong_task_id: int = -2

        with self.assertRaises(AssertionError) as context:
            self._es_wrong_user_id: ExecutionSubspace = ExecutionSubspace(_wrong_user_id,
                                                                          self._task_id, self._algorithms,
                                                                          self._subspace, self._result_path,
                                                                          self._subspace_dtype, self.__cache_dataset,
                                                                          self.__on_execution_element_finished)

        with self.assertRaises(AssertionError) as context:
            self._es_wrong_task_id: ExecutionSubspace = ExecutionSubspace(self._user_id,
                                                                          _wrong_task_id, self._algorithms,
                                                                          self._subspace, self._result_path,
                                                                          self._subspace_dtype, self.__cache_dataset,
                                                                          self.__on_execution_element_finished)

    def test_generate_execution_elements(self):
        # The method will be called on creation of ExecutionSubspace (in constructor -> just test outcome)
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


if __name__ == '__main__':
    unittest.main()
