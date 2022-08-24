import os
import unittest

import numpy as np

from backend.DataIO import DataIO
from backend.task.TaskErrorMessages import TaskErrorMessages
from backend.task.TaskHelper import TaskHelper
from backend.task.TaskState import TaskState
from backend.task.cleaning.DatasetCleaning import DatasetCleaning


class UnitTestDatasetCleaning(unittest.TestCase):
    _dir_name: str = os.getcwd()
    _uncleaned_dataset_path: str = os.path.join(_dir_name, "uncleaned_dataset.csv")
    _cleaned_dataset_path: str = os.path.join(_dir_name, "cleaned_dataset.csv")

    _user_id: int = -1
    _task_id: int = -1
    _priority: int = 9999

    _error_message: str = TaskErrorMessages().cleaning_result_empty
    _error_path: str = TaskHelper.convert_to_error_csv_path(_cleaned_dataset_path)

    def setUp(self) -> None:
        with open(self._uncleaned_dataset_path, 'w'):
            self._dc: DatasetCleaning = DatasetCleaning(self._user_id, self._task_id,
                                                        self.task_progress_callback,
                                                        "no_uncleaned_dataset",
                                                        self._cleaned_dataset_path, [],
                                                        self._priority)

    def tearDown(self) -> None:
        if os.path.isfile(self._error_path):
            os.remove(self._error_path)
        if os.path.isfile(self._uncleaned_dataset_path):
            os.remove(self._uncleaned_dataset_path)
        if os.path.isfile(self._cleaned_dataset_path):
            os.remove(self._cleaned_dataset_path)

    def test_empty_cleaning_result_handler(self):
        """Tests if __empty_cleaning_result_handler() works correctly"""
        self.assertFalse(os.path.isfile(self._error_path))

        # array not empty
        not_empty: np.ndarray = np.asarray(["I am not empty (:"])
        self.assertFalse(
            self._dc._DatasetCleaning__empty_cleaning_result_handler(not_empty))
        self.assertFalse(os.path.isfile(self._error_path))

        # array is empty
        empty: np.ndarray = np.asarray([])
        self.assertTrue(self._dc._DatasetCleaning__empty_cleaning_result_handler(empty))
        self.assertTrue(os.path.isfile(self._error_path))
        # compare error message
        self.assertEqual(self._error_message,
                         DataIO.read_uncleaned_csv(self._error_path, has_header=None)[
                             0][0])

        # clean up
        os.remove(self._error_path)
        self.assertFalse(os.path.isfile(self._error_path))

    def test_load_uncleaned_dataset(self):
        # No uncleaned Dataset -> throw exception
        with self.assertRaises(AssertionError):
            self._dc._DatasetCleaning__load_uncleaned_dataset()

    def test_create_with_nonempty_running_path(self):
        running_dataset_cleaning_path: str = "I.Am.Running"
        with open(self._uncleaned_dataset_path, 'w'):
            self._dc: DatasetCleaning = \
                DatasetCleaning(self._user_id, self._task_id,
                                self.task_progress_callback,
                                "no_uncleaned_dataset",
                                self._cleaned_dataset_path, [],
                                self._priority,
                                running_dataset_cleaning_path=
                                running_dataset_cleaning_path)
        self.assertEqual(self._dc._running_dataset_cleaning_path,
                         running_dataset_cleaning_path)

    def test_properties(self):
        self.assertEqual(self._dc._user_id, self._user_id)
        self.assertEqual(self._dc._task_id, self._task_id)
        self.assertEqual(self._dc._priority, self._priority)

    def task_progress_callback(self, _task_id: int, task_state: TaskState,
                               progress: float) -> None:
        return None  # empty callback


if __name__ == '__main__':
    unittest.main()
