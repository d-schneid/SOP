import os
import shutil
import unittest
import zipfile
from unittest import skip
from unittest.mock import Mock

import numpy as np

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.TaskHelper import TaskHelper
from backend.task.TaskState import TaskState
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from backend.task.execution.core.Execution import Execution


class SystemTest_Execution(unittest.TestCase):
    _user_id: int = 214
    _task_id: int = 1553

    _dataset_path: str = os.path.join(os.getcwd(), "./test/datasets/canada_climate_cleaned_to_compare.csv")

    _dir_name: str = os.getcwd()

    _result_path: str = "./test/system_tests/backend/task/execution/execution_folder_system_test1"
    _zipped_result_path: str = _result_path + ".zip"
    _details_path: str = os.path.join(_result_path, 'details.json')

    # subspace generation
    _subspace_size_min: int = 1
    _subspace_size_max: int = 5
    _subspace_amount = 4
    _subspace_seed = 42
    _data_dimensions_count: int = 26
    _subspace_generation: rsg = rsg(usd(_subspace_size_min, _subspace_size_max),
                                    _data_dimensions_count, _subspace_amount, _subspace_seed)

    # parameterized algorithms
    _algorithm_result: int = 42
    _hyper_parameter: dict = {'algorithm_result': _algorithm_result}
    _display_names: list[str] = ["display_name", "display_name", "different_display_name", "display_name"]
    _directory_names_in_execution: list[str] = ["display_name", "display_name (1)", "different_display_name",
                                                "display_name (2)"]

    _path: str = "./test/algorithms/DebugAlgorithm.py"
    _root_dir: str = "./test/"
    _algorithms: list[ParameterizedAlgorithm] = \
        list([ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[0]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[1]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[2]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[3])])

    _running_path = _result_path + ".I_am_running"
    _final_zip_path = _result_path + ".zip"

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        DebugScheduler()

        # Delete all folders and files of the old execution structure: BEFORE creating the new execution!
        self.__clear_old_execution_file_structure()

        # Reset callback variables
        self._started_running: bool = False
        self._metric_was_called: bool = False
        self._execution_finished: bool = False
        self._last_progress_report: float = 0
        AlgorithmLoader.set_algorithm_root_dir(self._root_dir)

        # create Execution
        self._ex = Execution(self._user_id, self._task_id,
                             self.__task_progress_callback, self._dataset_path,
                             self._result_path, self._subspace_generation,
                             iter(self._algorithms),
                             self.__metric_callback, 29221,
                             self._final_zip_path,
                             zip_running_path=self._zipped_result_path)

    def test_schedule_callbacks(self):
        # Test if all the callbacks where initialized correctly
        self.assertFalse(self._started_running)
        self.assertFalse(self._metric_was_called)
        self.assertFalse(self._execution_finished)
        self.assertEqual(0, self._last_progress_report)

        # perform the Execution
        self._ex.schedule()

        # Test if all the callbacks where performed
        self.assertTrue(self._started_running)
        self.assertTrue(self._metric_was_called)
        self.assertTrue(self._execution_finished)
        self.assertEqual(1, self._last_progress_report)

        # Clean up
        self.__clear_old_execution_file_structure()

    def test_schedule_result_folder(self):
        # The result folder does not exist yet
        self.assertFalse(os.path.exists(self._final_zip_path))

        # perform the Execution
        self._ex.schedule()

        # check if only the result folder exists (and is zipped)
        self.assertFalse(os.path.isdir(self._result_path))
        self.assertFalse(os.path.isdir(self._running_path))
        self.assertTrue(os.path.exists(self._final_zip_path))

        # Clean up
        self.__clear_old_execution_file_structure()

    @skip
    def test_schedule_result_folder_already_exists(self):
        """
        Do not perform the Execution when its result already exist
        """
        self.__clear_old_execution_file_structure()
        self._ex._Execution__unload_dataset = Mock(side_effect
                                                   =Exception("Scheduler was called -> Execution was started"))
        with self.assertRaises(Exception):
            self._ex.schedule()  # Scheduler was called because no Execution result exists

        # Create the result of Execution by hand
        _test_folder: str = self._result_path + "_test_folder"
        if os.path.exists(_test_folder):
            os.rmdir(_test_folder)
        os.mkdir(_test_folder)

        TaskHelper.zip_dir(_test_folder, self._running_path, self._zipped_result_path)
        self.assertTrue(os.path.exists(self._final_zip_path))

        # check if only the result folder exists (and is zipped)
        self.assertFalse(os.path.isdir(self._result_path))
        self.assertFalse(os.path.isdir(self._running_path))
        self.assertTrue(os.path.exists(self._final_zip_path))

        self._ex.schedule()  # No Exception -> Execution wasn't scheduled -> Execution was correctly skipped

        # Check callback result
        self.assertFalse(self._started_running)
        self.assertFalse(self._metric_was_called)
        self.assertTrue(self._execution_finished)
        self.assertEqual(1, self._last_progress_report)

        # Clean up
        self.__clear_old_execution_file_structure()

    def __clear_old_execution_file_structure(self):
        if os.path.isdir(self._result_path):
            shutil.rmtree(self._result_path)

        if os.path.exists(self._zipped_result_path):
            os.remove(self._zipped_result_path)

        if os.path.exists(self._final_zip_path):
            shutil.rmtree(self._final_zip_path)

        if os.path.exists(self._running_path):
            shutil.rmtree(self._running_path)

    def __task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        self.assertFalse(task_state.error_occurred())
        if task_state.is_running():
            self._started_running = True
        if task_state.is_finished():
            self._execution_finished = True

        # update progress
        self.assertTrue(progress >= self._last_progress_report)
        self._last_progress_report = progress

    def __metric_callback(self, execution: Execution) -> None:
        self._metric_was_called = True


if __name__ == '__main__':
    unittest.main()
