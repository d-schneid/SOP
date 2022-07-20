import os
import shutil
import unittest

import numpy as np

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
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

    _dataset_path: str = "./test/datasets/canada_climate_cleaned_to_compare.csv"

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
    _algorithm_result: np.ndarray = np.ndarray[[42]]
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

    _final_zip_path = _result_path + "final.zip"

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        DebugScheduler()

        # Delete all folders and files of the old execution structure: BEFORE creating the new execution!
        self.__clear_old_execution_file_structure()

        # Reset callback variables
        self._metric_was_called: bool = False
        self._started_running: bool = False
        self._execution_finished: bool = False
        self._last_progress_report: float = 0
        AlgorithmLoader.set_algorithm_root_dir(self._root_dir)
        # create Execution
        self._ex = Execution(self._user_id, self._task_id,
                             self.__task_progress_callback, self._dataset_path,
                             self._result_path, self._subspace_generation,
                             iter(self._algorithms),
                             self.__metric_callback, 29221,
                             self._final_zip_path)

    def test_schedule(self):
        self._ex.schedule()

        self.assertTrue(self._metric_was_called)
        self.assertTrue(self._started_running)
        self.assertTrue(self._execution_finished)
        self.assertEqual(1, self._last_progress_report)

    def __clear_old_execution_file_structure(self):
        if os.path.isdir(self._result_path):
            shutil.rmtree(self._result_path)

        if os.path.exists(self._zipped_result_path):
            os.remove(self._zipped_result_path)

        if os.path.exists(self._final_zip_path):
            os.remove(self._zipped_result_path)

        if os.path.exists(self._result_path + ".zip.running"):
            os.remove(self._result_path + ".zip.running")

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
