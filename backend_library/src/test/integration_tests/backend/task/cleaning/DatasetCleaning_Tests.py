import os
import unittest

import numpy as np

from backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend.task.TaskState import TaskState


class DatasetCleaningTestCleaningFinished(unittest.TestCase):
    """Tests if __did_cleaning_finish() works correctly when calling schedule()"""
    dir_name: str = os.getcwd()
    uncleaned_dataset_path: str = os.path.join(dir_name, "uncleaned_dataset.csv")
    cleaned_dataset_path: str = os.path.join(dir_name, "cleaned_dataset.csv")

    finished_cleaning: bool = False

    user_id: int = -1
    task_id: int = -1
    priority: int = 9999

    def setUp(self) -> None:
        with open(self.uncleaned_dataset_path, 'w') as uncleaned_csv:
            self._dc: DatasetCleaning = DatasetCleaning(self.user_id, self.task_id,
                                                        self.task_progress_callback, self.uncleaned_dataset_path,
                                                        self.cleaned_dataset_path, iter([]), self.priority)

    def tearDown(self) -> None:
        if os.path.isfile(self.uncleaned_dataset_path):
            os.remove(self.uncleaned_dataset_path)
        if os.path.isfile(self.cleaned_dataset_path):
            os.remove(self.cleaned_dataset_path)
        self._dc = None

    def test_is_DatasetCleaning_finished(self):
        # Cleaned file does not exist -> cleaning is NOT finished
        # Raise exception that scheduler does not exist
        with self.assertRaises(AssertionError):
            try:
                self._dc.schedule()
            except AttributeError:
                raise AssertionError
        self.assertFalse(self.finished_cleaning)

        # Cleaned file does exist -> cleaning is finished
        with open(self.cleaned_dataset_path, 'w') as cleaned_csv:
            self._dc.schedule()
            self.assertTrue(self.finished_cleaning)

    def task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        self.finished_cleaning = True


class DatasetCleaningTestNoUncleanedDataset(unittest.TestCase):
    """Tests if __did_cleaning_finish() works correctly when calling schedule()"""
    dir_name: str = os.getcwd()
    uncleaned_dataset_path: str = os.path.join(dir_name, "uncleaned_dataset.csv")
    cleaned_dataset_path: str = os.path.join(dir_name, "cleaned_dataset.csv")

    user_id: int = -1
    task_id: int = -1
    priority: int = 9999

    def setUp(self) -> None:
        with open(self.uncleaned_dataset_path, 'w') as uncleaned_csv:
            self._dc_missing_uncleaned_dataset: DatasetCleaning = DatasetCleaning(self.user_id, self.task_id,
                                                                                  self.task_progress_callback,
                                                                                  "no_uncleaned_dataset",
                                                                                  self.cleaned_dataset_path, iter([]),
                                                                                  self.priority)

    def tearDown(self) -> None:
        if os.path.isfile(self.uncleaned_dataset_path):
            os.remove(self.uncleaned_dataset_path)
        if os.path.isfile(self.cleaned_dataset_path):
            os.remove(self.cleaned_dataset_path)
        self._dc_missing_uncleaned_dataset = None

    def task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        pass

    def test_load_uncleaned_dataset(self):
        # No uncleaned Dataset -> throw exception
        with self.assertRaises(AssertionError) as context:
            self._dc_missing_uncleaned_dataset._DatasetCleaning__load_uncleaned_dataset()


if __name__ == '__main__':
    unittest.main()
