import os.path
import unittest
from collections.abc import Iterable
from unittest import mock

import numpy as np

from backend.task.execution.core.Execution import Execution as ex
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm


class ExecutionTest(unittest.TestCase):
    _user_id: int = 214
    _task_id: int = 1553
    _dataset_path: str = "dataset_path"

    _dir_name: str = os.getcwd()

    def __task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        # Empty callback
        pass

    def __metric_callback(self, execution: ex) -> None:
        # Empty callback
        pass

    def setUp(self) -> None:
        self._result_path: str = os.path.join(self._dir_name, "execution_folder")

        # subspace generation
        self._subspace_size_min: int = 1
        self._subspace_size_max: int = 5
        self._subspace_amount = 4
        self._subspace_seed = 42
        self._data_dimensions_count: int = 10
        self._subspace_generation: rsg = rsg(usd(self._subspace_size_min, self._subspace_size_max),
                                             self._data_dimensions_count, self._subspace_amount, self._subspace_seed)

        # parameterized algorithms
        self._hyper_parameter: dict = {'seed': 0}
        self._display_names: list[str] = ["display_name", "display_name", "different_display_name", "display_name"]
        self._directory_names_in_execution: list[str] = ["display_name", "display_name (1)", "different_display_name",
                                                         "display_name (2)"]

        self._algorithms: Iterable[ParameterizedAlgorithm] = \
            iter([ParameterizedAlgorithm("path", self._hyper_parameter, self._display_names[0]),
                  ParameterizedAlgorithm("path2", self._hyper_parameter, self._display_names[1]),
                  ParameterizedAlgorithm("path3", self._hyper_parameter, self._display_names[2]),
                  ParameterizedAlgorithm("path3", self._hyper_parameter, self._display_names[3])])

        # Delete all folders and files of the old execution structure: BEFORE creating the new execution!
        self.__clear_old_execution_file_structure()

        # create Execution
        self._ex = ex(self._user_id, self._task_id, self.__task_progress_callback, self._dataset_path,
                      self._result_path, self._subspace_generation, self._algorithms, self.__metric_callback)

    def tearDown(self) -> None:
        self._ex = None
        self._subspace_generation = None
        self._algorithms = None

        self.__clear_old_execution_file_structure()

    def test_getter(self):
        self.assertEqual(self._user_id, self._ex.user_id)
        self.assertEqual(self._user_id, self._ex.user_id)
        self.assertEqual(self._result_path, self._ex.result_path)
        self.assertEqual(self._algorithms, self._ex.algorithms)
        self.assertEqual(self._result_path + ".zip", self._ex.zip_result_path)

    def test_fill_algorithms_directory_name(self):
        iterable = self._ex._algorithms.__iter__()
        self.assertEqual(next(iterable).directory_name_in_execution, self._directory_names_in_execution[0])
        self.assertEqual(next(iterable).directory_name_in_execution, self._directory_names_in_execution[1])
        self.assertEqual(next(iterable).directory_name_in_execution, self._directory_names_in_execution[2])
        self.assertEqual(next(iterable).directory_name_in_execution, self._directory_names_in_execution[3])

    def test_generate_file_system_structure(self):
        self.assertTrue(os.path.isdir(self._result_path))
        for algorithm in self._algorithms:
            path: str = os.path.join(self._result_path, algorithm.display_name)
            self.assertTrue(os.path.isdir(path))

    def test_generate_execution_details_in_filesystem(self):
        details_path: str = os.path.join(self._result_path, 'details.json')
        self.assertTrue(os.path.isfile(details_path))

    def __clear_old_execution_file_structure(self):
        details_path: str = os.path.join(self._result_path, 'details.json')
        if os.path.isfile(details_path):
            os.remove(details_path)

        for dir_name in self._directory_names_in_execution:
            path: str = os.path.join(self._result_path, dir_name)
            if os.path.isdir(path):
                os.rmdir(path)
        if os.path.isdir(self._result_path):
            os.rmdir(self._result_path)


if __name__ == '__main__':
    unittest.main()
