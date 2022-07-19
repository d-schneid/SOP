import os.path
import shutil
import unittest
from unittest.mock import Mock

import numpy as np

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from backend.task.execution.core.Execution import Execution as ex
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.DataIO import DataIO


class UnitTestExecution(unittest.TestCase):

    _user_id: int = 214
    _task_id: int = 1553
    _priority: int = 1414

    _dataset_path: str = "dataset_path.csv"

    _dir_name: str = os.getcwd()

    _result_path: str = os.path.join(_dir_name, "execution_folder")
    _zipped_result_path: str = _result_path + ".zip"
    _details_path: str = os.path.join(_result_path, 'details.json')

    # subspace generation
    _subspace_size_min: int = 1
    _subspace_size_max: int = 5
    _subspace_amount = 4
    _subspace_seed = 42
    _data_dimensions_count: int = 10
    _subspace_generation: rsg = rsg(usd(_subspace_size_min, _subspace_size_max),
                                    _data_dimensions_count, _subspace_amount, _subspace_seed)

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

    _final_zip_path = _result_path + "final.zip"

    def __task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        # Empty callback
        pass

    def __metric_callback(self, execution: ex) -> None:
        # Empty callback
        pass

    def setUp(self) -> None:
        # Delete all folders and files of the old execution structure: BEFORE creating the new execution!
        self.__clear_old_execution_file_structure()

        # create Execution
        self._ex = ex(self._user_id, self._task_id, self.__task_progress_callback, self._dataset_path,
                      self._result_path, self._subspace_generation, iter(self._algorithms), self.__metric_callback,
                      self._final_zip_path, self._priority)

    def tearDown(self) -> None:
        self._ex = None

    def test_getter(self):
        self.assertEqual(self._algorithms, list(self._ex.algorithms))
        self.assertEqual(list(self._ex._subspaces), list(self._ex.subspaces))
        self.assertEqual(self._final_zip_path, self._ex.zip_result_path)
        self.assertEqual(self._priority, self._ex.priority)
        self.assertEqual(self._user_id, self._ex.user_id)
        self.assertEqual(self._task_id, self._ex.task_id)

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
        self.assertTrue(os.path.isfile(self._details_path))

    def test_does_zip_exists(self):
        if os.path.isdir(self._zipped_result_path):
            os.rmdir(self._zipped_result_path)

        self.assertFalse(os.path.exists(self._zipped_result_path))

        TaskHelper.create_directory(self._zipped_result_path)
        self.assertTrue(os.path.exists(self._zipped_result_path))

        os.rmdir(self._zipped_result_path)
        self.assertFalse(os.path.exists(self._zipped_result_path))

    def test_compute_progress(self):
        execution_element_count = self._subspace_amount * len(self._algorithms)

        for i in range(0, execution_element_count + 1):
            self._ex._finished_execution_element_count = i
            progress: float = i / execution_element_count
            progress *= 0.98
            if progress <= 0.98:
                self.assertAlmostEqual(progress, self._ex._Execution__compute_progress())
            else:
                self.assertAlmostEqual(0.98, self._ex._Execution__compute_progress())

        self._ex._metric_finished = True
        self.assertAlmostEqual(0.99, self._ex._Execution__compute_progress())

    def __clear_old_execution_file_structure(self):
        if os.path.isdir(self._result_path):
            shutil.rmtree(self._result_path)

        if os.path.exists(self._zipped_result_path):
            os.remove(self._zipped_result_path)

        if os.path.exists(self._final_zip_path):
            os.remove(self._zipped_result_path)

        if os.path.exists(self._result_path+".zip.running"):
            os.remove(self._result_path+".zip.running")

    def test_generate_execution_subspaces(self):
        _subspaces_count_in_execution_subspaces: int = 0
        _subspaces: list[Subspace] = list(self._ex.subspaces)

        # Check if method generates the right amount of execution subspaces
        self.assertEqual(0, len(self._ex._execution_subspaces))
        self._ex._Execution__generate_execution_subspaces()
        self.assertEqual(len(_subspaces), len(self._ex._execution_subspaces))

        # Check if method generates the correct execution subspaces (One for each subspace)
        for subspace in _subspaces:
            for execution_subspace in self._ex._execution_subspaces:
                if np.equal(execution_subspace._subspace.mask, subspace.mask).all():
                    _subspaces_count_in_execution_subspaces += 1
                    _subspaces.remove(subspace)
                    break

    def test_on_execution_element_finished_error_occurred_logic(self):
        self.assertEqual(False, self._ex._has_failed_element)

        self._ex._Execution__on_execution_element_finished(False)
        self.assertEqual(False, self._ex._has_failed_element)

        self._ex._Execution__on_execution_element_finished(True)
        self.assertEqual(True, self._ex._has_failed_element)

        self._ex._Execution__on_execution_element_finished(False)
        self.assertEqual(True, self._ex._has_failed_element)

    def test_on_execution_element_finished_finished_elements_logic(self):
        self._ex._Execution__unload_dataset = Mock(return_value=None)
        self._ex._Execution__schedule_result_zipping = Mock(return_value=None)

        self.assertFalse(self._ex._metric_finished)

        # normal logic -> increase _total_execution_element_count for each method call
        for i in range(0, self._ex._total_execution_element_count):
            self.assertEqual(i, self._ex._finished_execution_element_count)
            self._ex._Execution__on_execution_element_finished(False)
        self.assertEqual(self._ex._total_execution_element_count,
                         self._ex._finished_execution_element_count)

        self.assertEqual(False, self._ex._has_failed_element)
        self.assertTrue(self._ex._metric_finished)

        # out of range (more elements finished than elements exists)
        with self.assertRaises(AssertionError) as context:
            self._ex._Execution__on_execution_element_finished(True)

        # depending on how you look at it, you could not edit the error of Execution when the Exception ist raised
        # (but here we are applying it)
        self.assertEqual(True, self._ex._has_failed_element)

    def test_schedule_already_finished(self):
        Scheduler._instance = None

        # Finished file doesn't exist -> schedule this object -> raise TypeError because no scheduler exists
        with self.assertRaises(AssertionError) as context:
            self._ex.schedule()

        file_content: np.ndarray = np.asarray([["I am just a random value :D"]])
        DataIO.write_csv(self._final_zip_path, file_content)

        # Finished file does already exist -> don't schedule this object -> no Exception
        self._ex.schedule()

        os.remove(self._final_zip_path)


if __name__ == '__main__':
    unittest.main()
