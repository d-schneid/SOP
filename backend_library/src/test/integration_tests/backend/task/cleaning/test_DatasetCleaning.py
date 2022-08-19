import os
import unittest

import numpy as np

from backend.scheduler.Scheduler import Scheduler
from backend.task.TaskErrorMessages import TaskErrorMessages
from backend.task.TaskHelper import TaskHelper
from backend.task.TaskState import TaskState
from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from test.DatasetsForTesting import Datasets as ds


class IntegrationTestDatasetCleaning1(unittest.TestCase):
    _dir_name: str = os.getcwd()
    _uncleaned_dataset_path: str = os.path.join(_dir_name, "uncleaned_dataset.csv")
    _cleaned_dataset_path: str = os.path.join(_dir_name, "cleaned_dataset.csv")

    _finished_cleaning: bool = False

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999

    _error_message: str = TaskErrorMessages().cleaning_result_empty
    _error_path: str = TaskHelper.convert_to_error_csv_path(_cleaned_dataset_path)

    def setUp(self) -> None:
        with open(self._uncleaned_dataset_path, 'w') as uncleaned_csv:
            self._dc: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                        self.task_progress_callback,
                                                        self._uncleaned_dataset_path,
                                                        self._cleaned_dataset_path,
                                                        [], self._priority)
        self._finished_cleaning = False

    def tearDown(self) -> None:
        # cleanup
        if os.path.isfile(self._error_path):
            os.remove(self._error_path)
        if os.path.isfile(self._uncleaned_dataset_path):
            os.remove(self._uncleaned_dataset_path)
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)

    def test_is_DatasetCleaning_finished(self):
        """Tests if __did_cleaning_finish() works correctly when calling schedule()"""
        # Cleaned file does not exist -> cleaning is NOT finished
        # Raise exception that scheduler does not exist
        Scheduler._instance = None
        with self.assertRaises(AssertionError):
            try:
                self._dc.schedule()
            except AttributeError:
                raise AssertionError
        self.assertFalse(self._finished_cleaning)

        # Cleaned file does exist -> cleaning is finished
        with open(self._cleaned_dataset_path, 'w') as cleaned_csv:
            self._dc.schedule()
            self.assertTrue(self._finished_cleaning)
        os.remove(self._cleaned_dataset_path)

    def task_progress_callback(self, _task_id: int, task_state: TaskState,
                               progress: float) -> None:
        if task_state.is_finished():
            self._finished_cleaning = True


class IntegrationTestDatasetCleaningNoUncleanedDataset(unittest.TestCase):
    """Tests if __did_cleaning_finish() works correctly when calling schedule()"""
    _dir_name: str = os.getcwd()
    _uncleaned_dataset_path: str = os.path.join(_dir_name, "uncleaned_dataset.csv")
    _cleaned_dataset_path: str = os.path.join(_dir_name, "cleaned_dataset.csv")

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999

    def setUp(self) -> None:
        with open(self._uncleaned_dataset_path, 'w') as uncleaned_csv:
            self._dc_missing_uncleaned_dataset: DatasetCleaning = DatasetCleaning(
                self._user_id, self._task_id,
                self.task_progress_callback,
                "no_uncleaned_dataset",
                self._cleaned_dataset_path, [],
                self._priority)

    def tearDown(self) -> None:
        if os.path.isfile(self._uncleaned_dataset_path):
            os.remove(self._uncleaned_dataset_path)
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)
        self._dc_missing_uncleaned_dataset = None

    def test_load_uncleaned_dataset(self):
        # No uncleaned Dataset -> throw exception
        with self.assertRaises(AssertionError):
            self._dc_missing_uncleaned_dataset. \
                _DatasetCleaning__load_uncleaned_dataset()

    def task_progress_callback(self, _task_id: int, task_state: TaskState,
                               progress: float) -> None:
        pass


class IntegrationTestDatasetCleaningRunCleaningPipeline(unittest.TestCase):
    _dir_name: str = os.getcwd()
    # dataset 1
    _uncleaned_dataset_path: str = os.path.join(_dir_name,
                                                "uncleaned_dataset1.csv.error")
    _cleaned_dataset_path: str = os.path.join(_dir_name, "cleaned_dataset1.csv")

    _uncleaned_dataset1: np.ndarray = ds().cat_dataset3
    _cleaned_dataset1_data: np.ndarray = np.asarray([[0., 0.]])
    _cleaned_dataset1: np.ndarray = \
        np.asarray([['', '0', '1'],
                    [0, 0., 0.]], object)

    # dataset 2
    _uncleaned_dataset2: np.ndarray = ds().big_dataset1

    _finished_cleaning: bool = False

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999

    def task_progress_callback(self, _task_id: int, task_state: TaskState,
                               progress: float) -> None:
        self.assertTrue(task_state.is_running())
        self.assertTrue(progress >= 0)
        self.assertTrue(progress < 1)  # Is smaller than one in run_pipeline

    def setUp(self) -> None:
        self._ds = ds()

        self.__clean_created_files_and_directories()
        with open(self._uncleaned_dataset_path, 'w') as uncleaned_csv:
            self._dc: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                        self.task_progress_callback,
                                                        self._uncleaned_dataset_path,
                                                        self._cleaned_dataset_path,
                                                        None, self._priority)

    def __clean_created_files_and_directories(self):
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)
        if os.path.isfile(self._cleaned_dataset_path + ".error"):
            os.remove(self._cleaned_dataset_path + ".error")
        if os.path.isfile(self._uncleaned_dataset_path):
            os.remove(self._uncleaned_dataset_path)

    def test_run_cleaning_pipeline1(self):
        np.testing.assert_array_equal(self._cleaned_dataset1_data,
                                      self._dc._DatasetCleaning__run_cleaning_pipeline
                                      (self._ds.data_to_annotated
                                       (self._uncleaned_dataset1)).data)
        np.testing.assert_array_equal(self._cleaned_dataset1,
                                      self._dc._DatasetCleaning__run_cleaning_pipeline
                                      (self._ds.data_to_annotated
                                       (self._uncleaned_dataset1)).to_single_array())

    def test_run_cleaning_pipeline2(self):
        cleaned_dataset2_data: np.ndarray = np.asarray(
            [[0.00000000e+00, 1.00000000e+00, 0.00000000e+00, 1.00000000e+00,
              0.00000000e+00, 1.00000000e+00, 1.00000000e+00],
             [1.00000000e+00, 5.00405186e-01, 1.00000000e+00, 0.00000000e+00,
              8.12019199e-02, 1.32896857e-06, 0.00000000e+00],
             [6.07124844e-05, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
              1.00000000e+00, 0.00000000e+00, 9.87870182e-01],
             [6.07124844e-05, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
              1.00000000e+00, 0.00000000e+00, 9.87870182e-01]])
        np.testing.assert_array_almost_equal(cleaned_dataset2_data,
                                             self._dc
                                             ._DatasetCleaning__run_cleaning_pipeline
                                             (self._ds.data_to_annotated
                                              (self._uncleaned_dataset2)).data)

        cleaned_dataset2_header: np.ndarray = np.asarray(
            ['0', '1', '2', '3', '4', '7', '8'])
        np.testing.assert_array_equal(cleaned_dataset2_header,
                                      self._dc
                                      ._DatasetCleaning__run_cleaning_pipeline
                                      (self._ds.data_to_annotated
                                       (self._uncleaned_dataset2)).headers)

        cleaned_dataset2_row_mapping: np.ndarray = np.asarray(
            [0, 1, 2, 4])
        np.testing.assert_array_equal(cleaned_dataset2_row_mapping,
                                      self._dc
                                      ._DatasetCleaning__run_cleaning_pipeline
                                      (self._ds.data_to_annotated
                                       (self._uncleaned_dataset2)).row_mapping)


if __name__ == '__main__':
    unittest.main()
