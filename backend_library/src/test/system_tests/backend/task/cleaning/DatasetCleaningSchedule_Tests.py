import os
import unittest

import numpy as np

from backend.task.TaskState import TaskState
from test.DatasetsForTesting import Datasets as ds
from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend.scheduler.DebugScheduler import DebugScheduler
from backend.scheduler.Scheduler import Scheduler
from backend.DataIO import DataIO


class DatasetCleaningTestRunCleaningPipeline(unittest.TestCase):
    # DatasetCleaning object constructor variables
    _finished_cleaning: bool = False

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999

    # datasets
    _dir_name: str = os.getcwd()

    # dataset 1
    _uncleaned_dataset_path1: str = os.path.join(_dir_name, "uncleaned_dataset1.csv")
    _cleaned_dataset_path1: str = os.path.join(_dir_name, "cleaned_dataset1.csv")

    _uncleaned_dataset1: np.ndarray = ds().cat_dataset3
    _cleaned_dataset1: np.ndarray = np.asarray([[0., 0.]])

    # dataset 2
    _uncleaned_dataset_path2: str = os.path.join(_dir_name, "uncleaned_dataset2.csv")
    _cleaned_dataset_path2: str = os.path.join(_dir_name, "cleaned_dataset2.csv")

    _uncleaned_dataset2: np.ndarray = ds().big_dataset1

    # dataset 3: canada_climate.csv
    _uncleaned_dataset_path3: str = "test/datasets/canada_climate_uncleaned.csv"
    _cleaned_dataset_path3: str = "test/datasets/canada_climate_cleaned.csv"


    def task_progress_callback(self, _task_id: int, task_state: TaskState, progress: float) -> None:
        pass

    def setUp(self) -> None:
        # Scheduler
        Scheduler._instance = None
        DebugScheduler()

        # DatasetCleaning creation
        self.__clean_created_files_and_directories()

        self._dataIO = DataIO()
        self._dataIO.write_csv(self._uncleaned_dataset_path1, self._uncleaned_dataset1)
        self._dataIO.write_csv(self._uncleaned_dataset_path2, self._uncleaned_dataset2)

        self._dc1: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                     self.task_progress_callback, self._uncleaned_dataset_path1,
                                                     self._cleaned_dataset_path1, None, self._priority)

        self._dc2: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                     self.task_progress_callback, self._uncleaned_dataset_path2,
                                                     self._cleaned_dataset_path2, None, self._priority)

        self._dc3: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                     self.task_progress_callback, self._uncleaned_dataset_path3,
                                                     self._cleaned_dataset_path3, None, self._priority)

    def tearDown(self) -> None:
        self.__clean_created_files_and_directories()
        self._dc1 = None
        self._dc2 = None
        self._dc3 = None

    def __clean_created_files_and_directories(self):
        # dataset 1
        if os.path.isfile(self._cleaned_dataset_path1):
            os.remove(self._cleaned_dataset_path1)
        if os.path.isfile(self._cleaned_dataset_path1 + ".error"):
            os.remove(self._cleaned_dataset_path1 + ".error")
        if os.path.isfile(self._uncleaned_dataset_path1):
            os.remove(self._uncleaned_dataset_path1)
        # dataset 2
        if os.path.isfile(self._cleaned_dataset_path2):
            os.remove(self._cleaned_dataset_path2)
        if os.path.isfile(self._cleaned_dataset_path2 + ".error"):
            os.remove(self._cleaned_dataset_path2 + ".error")
        if os.path.isfile(self._uncleaned_dataset_path2):
            os.remove(self._uncleaned_dataset_path2)
        # dataset 3
        if os.path.isfile(self._cleaned_dataset_path3 + ".error"):
            os.remove(self._cleaned_dataset_path3 + ".error")

    def test_run_cleaning_pipeline1(self):
        self._dc1.schedule()
        np.testing.assert_array_almost_equal(self._cleaned_dataset1,
                                             DataIO.read_cleaned_csv(self._cleaned_dataset_path1))

    def test_run_cleaning_pipeline2(self):
        self._dc2.schedule()
        cleaned_dataset2: np.ndarray = np.asarray([[0.00000000e+00, 1.00000000e+00, 0.00000000e+00, 1.00000000e+00,
                                                    0.00000000e+00, 1.00000000e+00, 1.00000000e+00],
                                                   [1.00000000e+00, 5.00405186e-01, 1.00000000e+00, 0.00000000e+00,
                                                    8.12019199e-02, 1.32896857e-06, 0.00000000e+00],
                                                   [6.07124844e-05, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                                                    1.00000000e+00, 0.00000000e+00, 9.87870182e-01],
                                                   [6.07124844e-05, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                                                    1.00000000e+00, 0.00000000e+00, 9.87870182e-01]])
        np.testing.assert_array_almost_equal(cleaned_dataset2, DataIO.read_cleaned_csv(self._cleaned_dataset_path2))

    def test_run_cleaning_pipeline3(self):
        self._dc3.schedule()
        print(DataIO.read_cleaned_csv(self._cleaned_dataset_path3))
        cleaned_dataset3: np.ndarray = DataIO.read_cleaned_csv(self._cleaned_dataset_path3)
        np.testing.assert_array_almost_equal(cleaned_dataset3, DataIO.read_cleaned_csv(self._cleaned_dataset_path3))


if __name__ == '__main__':
    unittest.main()
