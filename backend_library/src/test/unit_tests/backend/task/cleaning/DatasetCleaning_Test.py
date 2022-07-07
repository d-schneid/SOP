import os
import unittest

from backend_library.src.main.backend.task.cleaning.DatasetCleaning import DatasetCleaning
from backend_library.src.main.backend.task.TaskState import TaskState


class DatasetCleaningTestCleaningFinished(unittest.TestCase):
    dir_name: str = os.getcwd()
    original_dataset_path: str = os.path.join(dir_name, "uncleaned_dataset.csv")
    cleaned_dataset_path: str = os.path.join(dir_name, "cleaned_dataset.csv")

    finished_cleaning: bool = False

    user_id: int = -13113
    task_id: int = -2143
    priority: int = 9999

    def setUp(self) -> None:
        with open(self.original_dataset_path, 'w') as uncleaned_csv:
            self._dc: DatasetCleaning = DatasetCleaning(self.user_id, self.task_id,
                                                        self.task_progress_callback, self.original_dataset_path,
                                                        self.cleaned_dataset_path, iter([]), self.priority)

    def tearDown(self) -> None:
        if os.path.isfile(self.original_dataset_path):
            os.remove(self.original_dataset_path)
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

    def test_getter(self):
        self.assertEqual(self.user_id, self._dc.user_id)
        self.assertEqual(self.task_id, self._dc.task_id)
        self.assertEqual(self.priority, self._dc.priority)


class DatasetCleaningTestDoWork(unittest.TestCase):
    dir_name: str = os.getcwd()
    original_dataset_path: str = os.path.join(dir_name, "uncleaned_dataset.csv")
    cleaned_dataset_path: str = os.path.join(dir_name, "cleaned_dataset.csv")

    finished_cleaning: bool = False

    user_id: int = -13113
    task_id: int = -2143
    priority: int = 9999

    def setUp(self) -> None:
        with open(self.original_dataset_path, 'w') as uncleaned_csv:
            self._dc: DatasetCleaning = DatasetCleaning(self.user_id, self.task_id,
                                                        self.task_progress_callback, self.original_dataset_path,
                                                        self.cleaned_dataset_path, iter([]), self.priority)

    def tearDown(self) -> None:
        if os.path.isfile(self.original_dataset_path):
            os.remove(self.original_dataset_path)
        if os.path.isfile(self.cleaned_dataset_path):
            os.remove(self.cleaned_dataset_path)
        self._dc = None

    def task_progress_callback(self, task_id: int, task_state: TaskState, progress: float) -> None:
        # Implement
        pass

    def test_delete_old_error_file(self):
        # TODO
        pass

    def test_empty_to_clean(self):
        """
        Test cleaning an empty dataset -> Write error csv
        (original dataset is empty)
        """
        self._dc.do_work()
        # TODO CHECK FOR ERROR FILE


if __name__ == '__main__':
    unittest.main()

