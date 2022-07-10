import os.path
import unittest

from backend.task.execution.core.Execution import Execution as ex
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm

from backend.scheduler.DebugScheduler import DebugScheduler


class ExecutionTestResultZipping(unittest.TestCase):
    _user_id: int = 214
    _task_id: int = 1553
    _dataset_path: str = "dataset_path.csv"

    _dir_name: str = os.getcwd()

    def __task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        # Empty callback
        pass

    def __metric_callback(self, execution: ex) -> None:
        # Empty callback
        pass

    def setUp(self) -> None:
        self._result_path: str = os.path.join(self._dir_name, "execution_folder")
        self._zipped_result_path: str = self._result_path + ".zip"

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

        self._algorithms: list[ParameterizedAlgorithm] = \
            list([ParameterizedAlgorithm("path", self._hyper_parameter, self._display_names[0]),
                  ParameterizedAlgorithm("path2", self._hyper_parameter, self._display_names[1]),
                  ParameterizedAlgorithm("path3", self._hyper_parameter, self._display_names[2]),
                  ParameterizedAlgorithm("path3", self._hyper_parameter, self._display_names[3])])

        # Delete all folders and files of the old execution structure: BEFORE creating the new execution!
        self.__clear_old_execution_file_structure()

        # create Execution
        self._ex = ex(self._user_id, self._task_id, self.__task_progress_callback, self._dataset_path,
                      self._result_path, self._subspace_generation, iter(self._algorithms), self.__metric_callback)

        # create a DebugScheduler
        DebugScheduler()

    def tearDown(self) -> None:
        self._ex = None
        self._subspace_generation = None
        self._algorithms = None

        self.__clear_old_execution_file_structure()

    def test_schedule_result_zipping(self):
        self.assertFalse(os.path.exists(self._zipped_result_path))
        self._ex._Execution__schedule_result_zipping()
        self.assertTrue(os.path.exists(self._zipped_result_path))
        os.rmdir(self._zipped_result_path)

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

        if os.path.isdir(self._zipped_result_path):
            os.rmdir(self._zipped_result_path)


if __name__ == '__main__':
    unittest.main()
