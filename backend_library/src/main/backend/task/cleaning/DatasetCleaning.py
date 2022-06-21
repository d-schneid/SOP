import os
import numpy as np
import string
from typing import List

import DatasetCleaningStep

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.DataIO import DataIO

from collections.abc import Callable


array = np.array([1, 2, 3, 3.0, None])
print(array.dtype)


array2 = np.array([[1, 2.], [2, 3.], [None, 1]])
print(array2.dtype)

print(np.dtype(np.float32))

# array3 = np.array(np.float32(1.0), np.float32(31.0), np.float32(121.0))
array3 = np.float32([(1.0, 23.), (31.0,321), (121.0,123), (None, None)])
print(array3.dtype)
print(array3[3])



class DatasetCleaning(Task):
    original_dataset_path: string
    cleaned_dataset_path: string
    cleaning_steps = []  # DatasetCleaningStep[]

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable, original_dataset_path: string,
                 cleaned_dataset_path: string, cleaning_steps):
        Task.__init__(user_id, task_id, task_progress_callback)
        self.original_dataset_path = original_dataset_path
        self.cleaned_dataset_path = cleaned_dataset_path
        self.cleaning_steps = cleaning_steps

    def schedule(self) -> None:
        if self.did_cleaning_finish(self):
            self.task_progress_callback(self.task_id, TaskState.FINISHED, 1.0)
            return None
        # TODO: Insert into Scheduler
        return None

    def did_cleaning_finish(self) -> bool:
        return os.path.isfile(self.cleaned_dataset_path)

    # scheduling
    def get_user_id(self) -> int:
        return self.user_id

    def do_work(self) -> None:
        # TODO Implement
        csv_to_clean = self.load_original_dataset()
        self.run_cleaning_pipeline(csv_to_clean)
        return None

    def load_original_dataset(self):
        uncleaned_dataset: np.object = DataIO.read_uncleaned_csv(self.original_dataset_path)
        # TODO Implement Test
        return None

    def run_cleaning_pipeline(self, csv_to_clean) -> None:
        finished_cleaning_steps: int = 0

        for cleaning_step in self.cleaning_steps:
            try:
                cleaning_step.do_cleaning(csv_to_clean)
            except:  # catch *all* exceptions
                # TODO: Write CSV File with exception-content (with .error suffix)
                self.progress_update_callback(self.task_id, TaskState.FINISHED_WITH_ERROR, 1)
                return None

            finished_cleaning_steps += 1
            progress: float = finished_cleaning_steps / len(self.cleaning_steps)
            self.progress_update_callback(self.task_id, TaskState.RUNNING, progress)

        self.progress_update_callback(self.task_id, TaskState.FINISHED, 1)
        # TODO: Implement Test

    def is_float_csv(self, csv_to_check) -> bool:
        type = csv_to_check.dtype
        if type == np.float32 or type == np.int32:
            return True
        return False
        # TODO: Implement Test

    def store_cleaned_dataset(self, cleaned_dataset) -> None:
        DataIO.write_csv(self.cleaned_dataset_path, cleaned_dataset)
        # TODO Implement Test
        return None


