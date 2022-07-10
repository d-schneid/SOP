import os
import unittest

import numpy as np

from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper
from backend.DataIO import DataIO
from backend.task.TaskErrorMessages import TaskErrorMessages
from backend_library.src.test.DatasetsForTesting import Datasets as ds


class DatasetCleaningTest1(unittest.TestCase):
    _dir_name: str = os.getcwd()
    _un_cleaned_dataset_path: str = os.path.join(_dir_name, "uncleaned_dataset.csv")
    _cleaned_dataset_path: str = os.path.join(_dir_name, "cleaned_dataset.csv")

    _finished_cleaning: bool = False

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999

    _error_message: str = TaskErrorMessages().cleaning_result_empty
    _error_path: str = TaskHelper.convert_to_error_csv_path(_cleaned_dataset_path)

    def setUp(self) -> None:
        self.__clean_created_files_and_directories()
        with open(self._un_cleaned_dataset_path, 'w') as uncleaned_csv:
            self._dc: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                        self.task_progress_callback, self._un_cleaned_dataset_path,
                                                        self._cleaned_dataset_path, iter([]), self._priority)

    def tearDown(self) -> None:
        self.__clean_created_files_and_directories()
        self._dc = None

    def test_is_DatasetCleaning_finished(self):
        """Tests if __did_cleaning_finish() works correctly when calling schedule()"""
        # Cleaned file does not exist -> cleaning is NOT finished
        # Raise exception that scheduler does not exist
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

    def test_empty_cleaning_result_handler(self):
        """Tests if __empty_cleaning_result_handler() works correctly"""
        self.assertFalse(os.path.isfile(self._error_path))

        # array not empty
        not_empty: np.ndarray = np.asarray(["I am not empty (:"])
        self.assertFalse(self._dc._DatasetCleaning__empty_cleaning_result_handler(not_empty))
        self.assertFalse(os.path.isfile(self._error_path))

        # array is empty
        empty: np.ndarray = np.asarray([])
        self.assertTrue(self._dc._DatasetCleaning__empty_cleaning_result_handler(empty))
        self.assertTrue(os.path.isfile(self._error_path))
        # compare error message
        self.assertEqual(self._error_message, DataIO.read_uncleaned_csv(self._error_path)[0][0])

        # clean up
        os.remove(self._error_path)
        self.assertFalse(os.path.isfile(self._error_path))

    def task_progress_callback(self, _task_id: int, task_state: TaskState, progress: float) -> None:
        self._finished_cleaning = True

    def __clean_created_files_and_directories(self):
        if os.path.isfile(self._error_path):
            os.remove(self._error_path)
        if os.path.isfile(self._un_cleaned_dataset_path):
            os.remove(self._un_cleaned_dataset_path)
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)


class DatasetCleaningTestNoUncleanedDataset(unittest.TestCase):
    """Tests if __did_cleaning_finish() works correctly when calling schedule()"""
    _dir_name: str = os.getcwd()
    _un_cleaned_dataset_path: str = os.path.join(_dir_name, "uncleaned_dataset.csv")
    _cleaned_dataset_path: str = os.path.join(_dir_name, "cleaned_dataset.csv")

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999

    def setUp(self) -> None:
        with open(self._un_cleaned_dataset_path, 'w') as uncleaned_csv:
            self._dc_missing_uncleaned_dataset: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                                                  self.task_progress_callback,
                                                                                  "no_uncleaned_dataset",
                                                                                  self._cleaned_dataset_path, iter([]),
                                                                                  self._priority)

    def tearDown(self) -> None:
        if os.path.isfile(self._un_cleaned_dataset_path):
            os.remove(self._un_cleaned_dataset_path)
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)
        self._dc_missing_uncleaned_dataset = None

    def test_load_uncleaned_dataset(self):
        # No uncleaned Dataset -> throw exception
        with self.assertRaises(AssertionError) as context:
            self._dc_missing_uncleaned_dataset._DatasetCleaning__load_uncleaned_dataset()

    def task_progress_callback(self, _task_id: int, task_state: TaskState, progress: float) -> None:
        pass


class DatasetCleaningTestRunCleaningPipeline(unittest.TestCase):
    _dir_name: str = os.getcwd()
    _uncleaned_dataset_path1: str = os.path.join(_dir_name, "uncleaned_dataset1.csv")
    _cleaned_dataset_path1: str = os.path.join(_dir_name, "cleaned_dataset1.csv")

    _uncleaned_dataset1: np.ndarray = ds().cat_dataset3
    _cleaned_dataset1: np.ndarray = np.asarray([1., 1.])

    _finished_cleaning: bool = False

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999



    def task_progress_callback1(self, _task_id: int, task_state: TaskState, progress: float) -> None:
        pass

    def setUp(self) -> None:
        self.__clean_created_files_and_directories()
        with open(self._uncleaned_dataset_path1, 'w') as uncleaned_csv:
            self._dc1: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                         self.task_progress_callback1, self._uncleaned_dataset_path1,
                                                         self._cleaned_dataset_path1, None, self._priority)

    def tearDown(self) -> None:
        self.__clean_created_files_and_directories()
        self._dc1 = None

    def __clean_created_files_and_directories(self):
        if os.path.isfile(self._cleaned_dataset_path1):
            os.remove(self._cleaned_dataset_path1)
        if os.path.isfile(self._uncleaned_dataset_path1):
            os.remove(self._uncleaned_dataset_path1)

    def test_run_cleaning_pipeline1(self):
        np.testing.assert_array_equal(self._cleaned_dataset1,
                                      self._dc1._DatasetCleaning__run_cleaning_pipeline(self._uncleaned_dataset1))


if __name__ == '__main__':
    unittest.main()
