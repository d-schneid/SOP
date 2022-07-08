import unittest
from collections.abc import Iterable
from unittest import mock

from backend_library.src.main.backend.task.execution.core.Execution import Execution as ex
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend_library.src.main.backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm


class ExecutionTest(unittest.TestCase):
    _user_id: int = 214
    _task_id: int = 1553
    _dataset_path: str = "dataset_path"
    _result_path: str = "result_path"

    def __task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        # Empty callback
        pass

    def __metric_callback(self, execution: ex) -> None:
        # Empty callback
        pass

    def setUp(self) -> None:
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
        self._algorithms: Iterable[ParameterizedAlgorithm] = \
            iter([ParameterizedAlgorithm("path", self._hyper_parameter, "display_name")])

        # create Execution
        self._ex = ex(self._user_id, self._task_id, self.__task_progress_callback, self._dataset_path,
                      self._result_path, self._subspace_generation, self._algorithms, self.__metric_callback)

    def tearDown(self) -> None:
        self._ex = None
        self._subspace_generation = None
        self._algorithms = None

    def test_getter(self):
        self.assertEqual(self._user_id, self._ex.user_id)
        self.assertEqual(self._user_id, self._ex.user_id)
        self.assertEqual(self._result_path, self._ex.result_path)
        self.assertEqual(self._algorithms, self._ex.algorithms)
        self.assertEqual(self._result_path + ".zip", self._ex.zip_result_path)


if __name__ == '__main__':
    unittest.main()
