import os.path
import shutil
import unittest
from unittest import skip

from backend.task.execution.core.Execution import Execution as ex
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler


class IntegrationTestExecutionResultZipping(unittest.TestCase):
    _user_id: int = 214
    _task_id: int = 1553
    _dataset_path: str = "dataset_path.csv"

    _dir_name: str = os.getcwd()

    # path creation
    _result_path: str = os.path.join(_dir_name, "execution_folder")
    _zipped_result_path: str = _result_path + ".zip"

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

    def __task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        pass  # Empty callback

    def __metric_callback(self, execution: ex) -> None:
        pass  # Empty callback

    def setUp(self) -> None:
        # create a DebugScheduler
        Scheduler._instance = None
        DebugScheduler()

        # Delete all folders and files of the old execution structure: BEFORE creating the new execution!
        self.__clear_old_execution_file_structure()

        # create Execution
        self._ex = ex(self._user_id, self._task_id, self.__task_progress_callback,
                      self._dataset_path,
                      self._result_path, self._subspace_generation,
                      iter(self._algorithms), self.__metric_callback)

    def tearDown(self) -> None:
        self.__clear_old_execution_file_structure()

    def test_schedule_result_zipping(self):
        self.assertFalse(os.path.exists(self._zipped_result_path))
        self._ex._Execution__schedule_result_zipping()
        self.assertTrue(os.path.exists(self._zipped_result_path))
        os.remove(self._zipped_result_path)

    def __clear_old_execution_file_structure(self):
        if os.path.isdir(self._result_path):
            shutil.rmtree(self._result_path)

        if os.path.exists(self._zipped_result_path):
            os.remove(self._zipped_result_path)


if __name__ == '__main__':
    unittest.main()
