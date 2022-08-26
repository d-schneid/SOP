import os
import unittest

from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.TaskState import TaskState
from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration as rsg
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution as usd
from backend.task.execution.core.Execution import Execution


class SystemTest_CleaningAndExecuting(unittest.TestCase):
    # for Cleaning and Execution #######################################################

    _cleaned_dataset_path: str = "./test/system_tests/backend/task/" \
                                 "cleaning_and_execution/" \
                                 "cleaned_dataset_for_execution.csv"

    _user_id: int = 214
    _task_id: int = 1553

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        self._rr_scheduler: DebugScheduler = DebugScheduler()

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

    def test_cleaning_and_execution(self):
        # Do the DatasetCleaning # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.assertFalse(os.path.isfile(self._cleaned_dataset_path))

        self._dc.schedule()

        self.assertTrue(os.path.isfile(self._cleaned_dataset_path))

        # Do the Execution # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.assertFalse(os.path.isfile(self._zipped_result_path))

        self._ex.schedule()

        self.assertTrue(os.path.isfile(self._zipped_result_path))

    # callbacks ########################################################################
    def __cleaning_task__progress_callback(self, task_id: int,
                                           task_state: TaskState, progress: float):
        pass

    def __execution_task_progress_callback(self, task_id: int,
                                           task_state: TaskState, progress: float):
        pass

    def __metric_callback(self, execution: Execution):
        pass

    # cleanup ##########################################################################
    def __cleanup_old_files(self):
        # DatasetCleaning
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)
        # Execution
        if os.path.isfile(self._result_path):
            os.remove(self._result_path)
        if os.path.isfile(self._zipped_result_path):
            os.remove(self._zipped_result_path)

    # setup ############################################################################
    def __setup_execution(self):
        # Execution setup ##############################################################

        self._result_path: str = "./test/system_tests/backend/task/" \
                                 "execution/basic_tests/execution_folder_system_test1"
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

        debug_algorithm_path: str = "./test/algorithms/DebugAlgorithm.py"
        knn_algorithm_path: str = "./test/algorithms/DebugAlgorithm.py"

        self._algorithms: list[ParameterizedAlgorithm] = \
            list([ParameterizedAlgorithm(debug_algorithm_path, hyper_parameter,
                                         "debug_algorithm"),
                  ParameterizedAlgorithm(knn_algorithm_path, knn_hyper_parameter,
                                         "KNN")])

        self._running_path = self._result_path + ".I_am_running"
        self._final_zip_path = self._result_path + ".zip"

    def __setup_cleaning(self):
        # DatasetCleaning setup ########################################################
        self._uncleaned_dataset_path: str = \
            "./test/datasets/canada_climate_uncleaned.csv"


if __name__ == '__main__':
    unittest.main()
