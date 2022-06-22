import csv
import os
import numpy as np
import string
from typing import List, Optional

import DatasetCleaningStep

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.DataIO import DataIO

from CategoricalColumnRemover import CategoricalColumnRemover
from ImputationMode import ImputationMode
from MinMaxScaler import MinMaxScaler

from collections.abc import Callable


class DatasetCleaning(Task):
    original_dataset_path: string
    cleaned_dataset_path: string
    cleaning_steps = []  # DatasetCleaningStep[]

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable, original_dataset_path: string,
                 cleaned_dataset_path: string, cleaning_steps=None):
        Task.__init__(self, user_id, task_id, task_progress_callback)
        if cleaning_steps is None:
            cleaning_steps = [CategoricalColumnRemover(), ImputationMode(), MinMaxScaler()]  # Default Cleaning-Pipeline
        self.original_dataset_path = original_dataset_path
        self.cleaned_dataset_path = cleaned_dataset_path
        self.cleaning_steps = cleaning_steps

    def schedule(self) -> None:
        if self.did_cleaning_finish():
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
        dataset_to_clean: np.ndarray = self.load_original_dataset()
        cleaning_pipeline_result: Optional[np.ndarray] = self.run_cleaning_pipeline(dataset_to_clean)
        if cleaning_pipeline_result is None:
            self.task_progress_callback(self.task_id, TaskState.FINISHED_WITH_ERROR, 1.0)
            return

        cleaned_dataset: np.ndarray = cleaning_pipeline_result.astype(
            np.float32)  # cast ndarray to float32 # TODO: Vllt copy=False

        if self.is_float_csv(cleaned_dataset):
            self.store_cleaned_dataset(cleaned_dataset)
            self.task_progress_callback(self.task_id, TaskState.FINISHED, 1.0)
        else:
            error_message: string = "Error: Type != float32 in cleaned_file"
            self.save_error_csv_file(error_message)
            self.task_progress_callback(self.task_id, TaskState.FINISHED_WITH_ERROR, 1.0)

    # do_work
    def load_original_dataset(self) -> np.ndarray:
        return DataIO.read_uncleaned_csv(self.original_dataset_path)

    def run_cleaning_pipeline(self, csv_to_clean) -> Optional[np.ndarray]:
        finished_cleaning_steps: int = 0

        for cleaning_step in self.cleaning_steps:
            try:
                if cleaning_step is not None:
                    csv_to_clean = cleaning_step.do_cleaning(csv_to_clean)
            except Exception as e:  # catch *all* exceptions
                self.save_error_csv_file(str(e))
                return None

            finished_cleaning_steps += 1
            progress: float = min(finished_cleaning_steps / len(self.cleaning_steps),
                                  0.99)  # compute and clamp progress
            self.task_progress_callback(self.task_id, TaskState.RUNNING, progress)

    @staticmethod
    def is_float_csv(csv_to_check) -> bool:
        dtype: np.dtype = csv_to_check.dtype
        if dtype == np.float32 or dtype == np.int32:
            return True
        return False

    def save_error_csv_file(self, error_message: string) -> None:
        error_file_path = self.cleaned_dataset_path + ".error"  # creates the path for the csv with the error message
        TaskHelper().save_error_csv(error_file_path, str(error_message))

    def store_cleaned_dataset(self, cleaned_dataset: np.ndarray) -> None:
        DataIO.write_csv(self.cleaned_dataset_path, cleaned_dataset)
