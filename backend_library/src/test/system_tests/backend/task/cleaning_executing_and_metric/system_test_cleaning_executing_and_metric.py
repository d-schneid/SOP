import os
import shutil
import unittest
from multiprocessing import Event

from backend.metric.MetricDataPointsAreOutliers import MetricDataPointsAreOutliers
from backend.metric.MetricSubspaceOutlierAmount import MetricSubspaceOutlierAmount
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.TaskState import TaskState
from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core.Execution import Execution
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from test.TestHelper import TestHelper

timeout = 720


class SystemTest_CleaningExecutingAndMetric(unittest.TestCase):
    # for Cleaning and Execution #######################################################

    _cleaned_dataset_path: str = "./test/system_tests/backend/task/" \
                                 "cleaning_executing_and_metric/" \
                                 "cleaned_dataset_for_execution.csv"

    _user_id: int = 214
    _task_id: int = 1553

    # precomputed
    _execution_result_folder_precomputed_path: str = \
        "./test/system_tests/backend/task/cleaning_executing_and_metric/" \
        "execution_result_folder_precomputed.zip"

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        self._rr_scheduler: Scheduler = UserRoundRobinScheduler()

        # Setup Algorithms
        alg_root_directory: str = "../resources/test"
        algorithm_loader: AlgorithmLoader = AlgorithmLoader()
        algorithm_loader.set_algorithm_root_dir(alg_root_directory)

        # Setup
        self.__setup_cleaning()
        self.__setup_execution()

        # Clean old Files
        self.__cleanup_old_files()

        # create DatasetCleaning
        self._dc: DatasetCleaning = \
            DatasetCleaning(self._user_id, self._task_id,
                            self.__cleaning_task__progress_callback,
                            self._uncleaned_dataset_path,
                            self._cleaned_dataset_path, None)

        # create Execution
        self._ex: Execution = Execution(self._user_id, self._task_id,
                                        self.__execution_task_progress_callback,
                                        self._cleaned_dataset_path,
                                        self._result_path, self._subspace_generation,
                                        self._algorithms,
                                        self.__metric_callback, 29221,
                                        self._final_zip_path,
                                        zip_running_path=self._zipped_result_path)

    def test_cleaning_execution_and_metric(self):
        # Do the DatasetCleaning # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.assertFalse(os.path.isfile(self._cleaned_dataset_path))

        self._dc.schedule()

        self.assertTrue(self._cleaning_finished.wait(timeout))
        self.assertTrue(os.path.isfile(self._cleaned_dataset_path))

        # Do the Execution # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.assertFalse(os.path.isfile(self._zipped_result_path))

        self._ex.schedule()

        self.assertTrue(self._execution_finished.wait(timeout))
        self.assertTrue(os.path.isfile(self._zipped_result_path))

        a_knn_execution_element_result_path: str = "/KNN/AAQAA.csv"
        metric_result1_path: str = "/metric/metric1.csv"

        self.assertTrue(TestHelper.is_same_execution_result_zip(
            self._execution_result_folder_precomputed_path, self._zipped_result_path,
            list([a_knn_execution_element_result_path, metric_result1_path])))

        # cleanup
        self.__cleanup_old_files()

    # callbacks ########################################################################
    def __cleaning_task__progress_callback(self, task_id: int,
                                           task_state: TaskState, progress: float):
        if task_state.is_finished():
            self._cleaning_finished.set()

    def __execution_task_progress_callback(self, task_id: int,
                                           task_state: TaskState, progress: float):
        if task_state.is_finished():
            self._execution_finished.set()

    def __metric_callback(self, execution: Execution):
        metric_folder_path: str = execution.result_path + "/metric"
        metric1_result_path: str = metric_folder_path + "/metric1.csv"
        metric2_result_path: str = metric_folder_path + "/metric2.csv"

        metric1: MetricDataPointsAreOutliers = \
            MetricDataPointsAreOutliers(self._ex.dataset_indices)
        metric2: MetricSubspaceOutlierAmount = \
            MetricSubspaceOutlierAmount()

        if not os.path.isdir(metric_folder_path):
            os.mkdir(metric_folder_path)

        metric1.compute_metric(metric1_result_path, self._ex.algorithm_directory_paths)
        metric2.compute_metric(metric2_result_path, self._ex.algorithm_directory_paths)

    # cleanup ##########################################################################
    def __cleanup_old_files(self):
        # DatasetCleaning
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)
        # Execution
        if os.path.isdir(self._result_path):
            shutil.rmtree(self._result_path)
        if os.path.isfile(self._zipped_result_path):
            os.remove(self._zipped_result_path)
        if os.path.isfile(self._zipped_result_path + "_unzipped"):
            os.remove(self._zipped_result_path + "_unzipped")
        if os.path.isfile(self._execution_result_folder_precomputed_path + "_unzipped"):
            os.remove(self._execution_result_folder_precomputed_path + "_unzipped")

    # setup ############################################################################
    def __setup_execution(self):
        # Execution setup ##############################################################

        self._result_path: str = "./test/system_tests/backend/task/" \
                                 "cleaning_executing_and_metric/execution_result_folder"
        self._zipped_result_path: str = self._result_path + ".zip"
        self._details_path: str = os.path.join(self._result_path, 'details.json')

        # subspace generation
        self._subspace_size_min: int = 1
        self._subspace_size_max: int = 5
        self._subspace_amount = 4
        self._subspace_seed = 42
        self._data_dimensions_count: int = 26
        self._subspace_generation: rsg = rsg(usd(self._subspace_size_min,
                                                 self._subspace_size_max),
                                             self._data_dimensions_count,
                                             self._subspace_amount,
                                             self._subspace_seed)

        # parameterized algorithms
        self._algorithm_result: int = 42
        hyper_parameter: dict = {'algorithm_result': self._algorithm_result}
        knn_hyper_parameter: dict = \
            {'contamination': 0.1,
             'n_neighbors': 5, 'method': 'largest',
             'radius': 1.0, 'algorithm': 'auto',
             'leaf_size': 30,
             'metric': 'minkowski', 'p': 2,
             'metric_params': None, 'n_jobs': 1}

        debug_algorithm_path: str = "../resources/test/algorithms/DebugAlgorithm.py"
        knn_algorithm_path: str = "../resources/test/algorithms/knn.py"

        self._algorithms: list[ParameterizedAlgorithm] = \
            list([ParameterizedAlgorithm(debug_algorithm_path, hyper_parameter,
                                         "debug_algorithm"),
                  ParameterizedAlgorithm(knn_algorithm_path, knn_hyper_parameter,
                                         "KNN")])

        self._running_path = self._result_path + ".I_am_running"
        self._final_zip_path = self._result_path + ".zip"

        self._execution_finished: Event = Event()

    def __setup_cleaning(self):
        # DatasetCleaning setup ########################################################
        self._uncleaned_dataset_path: str = \
            "../resources/test/datasets/canada_climate_uncleaned.csv"
        self._cleaning_finished: Event = Event()


if __name__ == '__main__':
    unittest.main()
