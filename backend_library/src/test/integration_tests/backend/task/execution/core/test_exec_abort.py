import os.path
import unittest

from backend.scheduler.Scheduler import Scheduler
from backend.task.TaskState import TaskState
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core.Execution import Execution as ex
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from test.UrrsWoWorkers import UrrsWoWorkers


class IntegrationTestExecutionAbort(unittest.TestCase):
    _dataset_path: str = os.path.join(
        os.getcwd(), "test/datasets/canada_climate_cleaned_to_compare.csv")

    # path creation
    _result_path: str = os.path.join(os.getcwd(), "execution_folder")
    _zipped_result_path: str = _result_path + ".zip"

    # subspace generation
    _subspace_generation: rsg = rsg(usd(26, 26), 26, 1, 42)
    _path: str = "./test/algorithms/IrrelevantPath.py"

    _algorithms: list[ParameterizedAlgorithm] = [
        ParameterizedAlgorithm(_path, {}, "abc")]

    def __task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        self.fail("No task progress callback should be send on abortions")

    def __metric_callback(self, execution: ex) -> None:
        pass  # Empty callback

    def setUp(self) -> None:
        # create a DebugScheduler
        Scheduler._instance = None
        UrrsWoWorkers()

        # create Execution
        self._ex = ex(-1, 1, self.__task_progress_callback,
                      self._dataset_path,
                      self._result_path, self._subspace_generation,
                      self._algorithms, self.__metric_callback, 29221)

    def tearDown(self) -> None:
        Scheduler.get_instance().hard_shutdown()
        Scheduler._instance = None

    def test_execution_abortion(self):
        self._ex.schedule()
        Scheduler.get_instance().abort_by_task(1)
        self.assertIsNone(self._ex._shared_memory_name)


if __name__ == '__main__':
    unittest.main()
