import string
from typing import List

import DatasetCleaningStep

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskState import TaskState

from collections.abc import Callable
#import numpy as np

class DatasetCleaning(Task):
    original_dataset_path: string
    cleaned_dataset_path: string
    cleaning_steps: List[DatasetCleaningStep] = []

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable, original_dataset_path: string,
                 cleaned_dataset_path: string, cleaning_steps: List[DatasetCleaningStep]):
        Task.__init__(user_id, task_id, task_progress_callback)
        self.original_dataset_path = original_dataset_path
        self.cleaned_dataset_path = cleaned_dataset_path
        self.cleaning_steps = cleaning_steps

    def did_cleaning_finish(self) -> bool:
        # TODO Implement
        return False

    # scheduling

    def get_user_id(self) -> int:
        return self.user_id

    def do_work(self) -> None:
        # TODO Implement
        return None

    def load_original_dataset(self):
        # TODO Implement
        return None

    def run_cleaning_pipeline(self, csv_to_clean) -> None:
        # TODO Implement
        # TODO Error Handling!! (Vorallem für Callback)

        finished_cleaning_steps: 0

        for cleaning_step in self.cleaning_steps:
            cleaning_step.do_cleaning()
            finished_cleaning_steps += 1
            progress: float = finished_cleaning_steps / len(self.cleaning_steps)
            self.progress_update_callback(self.task_id, TaskState.RUNNING, progress)
        self.progress_update_callback(self.task_id, TaskState.FINISHED, 1)

        return None

    def store_cleaned_dataset(self, cleaned_dataset) -> None:
        # TODO Implement
        return None