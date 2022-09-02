import os
import shutil
import unittest

from backend.metric.MetricDataPointsAreOutliers import MetricDataPointsAreOutliers
from backend.metric.MetricSubspaceOutlierAmount import MetricSubspaceOutlierAmount
from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from backend.task.TaskState import TaskState
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core.Execution import Execution
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from test.TestHelper import TestHelper


class SystemTest_ExecutionResultContents(unittest.TestCase):
    _user_id: int = 214
    _task_id: int = 1553

    _dataset_path: str = os.path.join(os.getcwd(),
                                      "../resources/test/datasets" +
                                      "/canada_climate_cleaned_to_compare.csv")

    _dir_name: str = os.getcwd()

    _result_path: str = "./test/system_tests/backend/task/" \
                        "execution/result_contents_tests" \
                        "/execution_system_test_result_contents"
    _zipped_result_path: str = _result_path + ".zip"
    _details_path: str = os.path.join(_result_path, 'details.json')
    _metric_path: str = _result_path + "/metric"

    # subspace generation
    _subspace_size_min: int = 1
    _subspace_size_max: int = 5
    _subspace_amount = 3
    _subspace_seed = 25  # funnier than 24
    _data_dimensions_count: int = 26
    _subspace_generation: rsg = rsg(usd(_subspace_size_min, _subspace_size_max),
                                    _data_dimensions_count, _subspace_amount,
                                    _subspace_seed)

    # parameterized algorithms
    _algorithm_result: int = 42
    _hyper_parameter: dict = {'algorithm_result': _algorithm_result}
    _display_names: list[str] = ["display_name", "display_name",
                                 "different_display_name", "display_name"]

    _path: str = "../resources/test/algorithms/DebugAlgorithm.py"
    _root_dir: str = "../resources/test/"
    _algorithms: list[ParameterizedAlgorithm] = \
        list([ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[0]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[1]),
              ParameterizedAlgorithm(_path, _hyper_parameter, _display_names[2])])

    _running_path: str = _result_path + ".I_am_running"
    _final_zip_path: str = _result_path + ".zip"

    # expected result
    _expected_execution_result: str = "./test/system_tests/backend/task/" \
                                      "execution/result_contents_tests" \
                                      "/execution_result_to_compare.zip"

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        DebugScheduler()

        # Delete all folders and files of the old execution structure:
        # BEFORE creating the new execution!
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
                             self._algorithms,
                             self.__metric_callback, 29221,
                             self._final_zip_path,
                             zip_running_path=self._zipped_result_path)

    def test_execution_result(self):
        """
        Runs a test execution with the Debug Algorithm and checks if the result folder
        contains all the necessary files. Also computes Metric and checks if the metric
        result is generated.
        """
        # Test if all the callbacks where initialized correctly
        self.assertFalse(self._started_running)
        self.assertFalse(self._metric_was_called)
        self.assertFalse(self._execution_finished)
        self.assertEqual(0, self._last_progress_report)

        # perform the Execution
        self._ex.schedule()
        # check if the result is correct (equals to the expected)
        self.assertTrue(TestHelper.is_same_execution_result_zip
                        (self._expected_execution_result, self._zipped_result_path,
                         list()))

        # Test if all the callbacks where performed
        self.assertTrue(self._started_running)
        self.assertTrue(self._metric_was_called)
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

    def __task_progress_callback(self, task_id: int,
                                 task_state: TaskState, progress: float) -> None:
        self.assertFalse(task_state.error_occurred())
        if task_state.is_running():
            self._started_running = True
        if task_state.is_finished():
            self._execution_finished = True

        # update progress
        self.assertGreaterEqual(progress, self._last_progress_report)
        self._last_progress_report = progress

    def __metric_callback(self, execution: Execution) -> None:
        if not os.path.isdir(self._metric_path):
            os.mkdir(self._metric_path)

        MetricDataPointsAreOutliers(self._ex.dataset_indices) \
            .compute_metric(self._metric_path + "/metric1.csv",
                            self._ex.algorithm_directory_paths)
        MetricSubspaceOutlierAmount.compute_metric(self._metric_path + "/metric2.csv",
                                                   self._ex.algorithm_directory_paths)

        self._metric_was_called = True


if __name__ == '__main__':
    unittest.main()
