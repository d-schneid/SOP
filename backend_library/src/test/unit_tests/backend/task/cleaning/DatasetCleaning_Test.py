import os
import unittest

import numpy as np
import pandas as pd

from backend_library.src.main.backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.task.TaskHelper import TaskHelper


class DatasetCleaningTestDoWork(unittest.TestCase):
    dir_name: str = os.getcwd()
    uncleaned_dataset_path: str = os.path.join(dir_name, "uncleaned_dataset.csv")
    cleaned_dataset_path: str = os.path.join(dir_name, "cleaned_dataset.csv")

    finished_cleaning: bool = False

    user_id: int = 1533
    task_id: int = 24
    priority: int = 9999

    def setUp(self) -> None:
        self._dc: DatasetCleaning = DatasetCleaning(self.user_id, self.task_id,
                                                    self.task_progress_callback, self.uncleaned_dataset_path,
                                                    self.cleaned_dataset_path, iter([]), self.priority)

        if os.path.isfile(self.uncleaned_dataset_path):
            os.remove(self.uncleaned_dataset_path)
        self._uncleaned_array: np.ndarray = np.asarray([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        pd.DataFrame(self._uncleaned_array).to_csv(self.uncleaned_dataset_path, index=False)

    def tearDown(self) -> None:
        if os.path.isfile(self.uncleaned_dataset_path):
            os.remove(self.uncleaned_dataset_path)
        if os.path.isfile(self.cleaned_dataset_path):
            os.remove(self.cleaned_dataset_path)
        self._dc = None

    def task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        # Empty callback
        pass

    def test_getter(self):
        self.assertEqual(self.user_id, self._dc.user_id)
        self.assertEqual(self.task_id, self._dc.task_id)
        self.assertEqual(self.priority, self._dc.priority)

    def test_did_cleaning_finish(self):
        if os.path.isfile(self.cleaned_dataset_path):
            os.remove(self.cleaned_dataset_path)

        self.assertFalse(self._dc._DatasetCleaning__did_cleaning_finish())

        with open(self.cleaned_dataset_path, 'w') as cleaned_csv:
            self.assertTrue(self._dc._DatasetCleaning__did_cleaning_finish())

        if os.path.isfile(self.cleaned_dataset_path):
            os.remove(self.cleaned_dataset_path)

        self.assertFalse(self._dc._DatasetCleaning__did_cleaning_finish())

    def test_delete_old_error_file(self):
        error_path = TaskHelper.convert_to_error_csv_path(self.cleaned_dataset_path)
        if os.path.isfile(error_path):
            os.remove(error_path)

        self._dc._DatasetCleaning__delete_old_error_file()
        self.assertFalse(os.path.isfile(error_path))

        with open(error_path, 'w') as cleaned_csv:
            self.assertTrue(os.path.isfile(error_path))

        # Test if it deletes the newly created error file:
        self._dc._DatasetCleaning__delete_old_error_file()
        self.assertFalse(os.path.isfile(error_path))

    def test_load_uncleaned_dataset(self):
        np.testing.assert_array_equal(self._dc._DatasetCleaning__load_uncleaned_dataset(),
                                      self._uncleaned_array)


class DatasetCleaningTestInvalidValues(unittest.TestCase):
    dir_name: str = os.getcwd()
    uncleaned_dataset_path: str = os.path.join(dir_name, "uncleaned_dataset.csv")
    cleaned_dataset_path: str = os.path.join(dir_name, "cleaned_dataset.csv")
    priority: int = 9999

    def task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        # Empty callback
        pass

    def test_invalid_user_id(self):
        # has to be >= 0

        # No Error:
        DatasetCleaning(-1, 0,
                        self.task_progress_callback, self.uncleaned_dataset_path,
                        self.cleaned_dataset_path, iter([]), self.priority)

        # <-1 -> exception
        with self.assertRaises(AssertionError) as context:
            DatasetCleaning(-2, 0,
                            self.task_progress_callback, self.uncleaned_dataset_path,
                            self.cleaned_dataset_path, iter([]), self.priority)

    def test_invalid_task_id(self):
        # has to be >= 0

        # No Error:
        DatasetCleaning(0, -1,
                        self.task_progress_callback, self.uncleaned_dataset_path,
                        self.cleaned_dataset_path, iter([]), self.priority)

        # <-1 -> exception
        with self.assertRaises(AssertionError) as context:
            DatasetCleaning(0, -2,
                            self.task_progress_callback, self.uncleaned_dataset_path,
                            self.cleaned_dataset_path, iter([]), self.priority)



if __name__ == '__main__':
    unittest.main()
