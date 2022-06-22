import os
import string
from collections.abc import Callable
from typing import Optional

import numpy as np

from CategoricalColumnRemover import CategoricalColumnRemover
from ImputationMode import ImputationMode
from MinMaxScaler import MinMaxScaler
from backend_library.src.main.backend.DataIO import DataIO
from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.task.TaskState import TaskState


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

    # scheduling #############################################
    def get_user_id(self) -> int:
        return self.user_id

    def get_task_id(self) -> int:
        return self.task_id

    def do_work(self) -> None:
        self.delete_old_error_file()

        dataset_to_clean: np.ndarray = self.load_original_dataset()
        cleaning_pipeline_result: Optional[np.ndarray] = self.run_cleaning_pipeline(dataset_to_clean)

        if cleaning_pipeline_result is None:  # cleaning failed
            self.task_progress_callback(self.task_id, TaskState.FINISHED_WITH_ERROR, 1.0)
            return

        cleaned_dataset: np.ndarray = cleaning_pipeline_result.astype(
            np.float32)  # cast ndarray to float32 # TODO: Vllt copy=False

        if TaskHelper.is_float_csv(cleaned_dataset):
            self.store_cleaned_dataset(cleaned_dataset)
            self.task_progress_callback(self.task_id, TaskState.FINISHED, 1.0)
        else:
            error_message: string = "Error: Type != float32 in cleaned_file"
            self.save_error_file(error_message)
            self.task_progress_callback(self.task_id, TaskState.FINISHED_WITH_ERROR, 1.0)

    # do_work #############################################
    def load_original_dataset(self) -> np.ndarray:
        return DataIO.read_uncleaned_csv(self.original_dataset_path)

    def run_cleaning_pipeline(self, csv_to_clean) -> Optional[np.ndarray]:
        finished_cleaning_steps: int = 0

        for cleaning_step in self.cleaning_steps:
            try:
                if cleaning_step is not None:
                    csv_to_clean = cleaning_step.do_cleaning(csv_to_clean)
            except Exception as e:  # catch *all* exceptions
                self.save_error_file(str(e))
                return None

            finished_cleaning_steps += 1
            progress: float = min(finished_cleaning_steps / len(self.cleaning_steps),
                                  0.99)  # compute and clamp progress
            self.task_progress_callback(self.task_id, TaskState.RUNNING, progress)

    def delete_old_error_file(self) -> None:
        error_file_path: string = TaskHelper().convert_to_error_csv_path(self.cleaned_dataset_path)
        if os.path.isfile(error_file_path):
            os.remove(error_file_path)

    # Saves the error_message as a csv file (error_file_path is given by TaskHelper.convert_to_error_csv_path())
    def save_error_file(self, error_message: string) -> None:
        error_file_path: string = TaskHelper.convert_to_error_csv_path(self.cleaned_dataset_path)
        TaskHelper.save_error_csv(error_file_path, error_message)

    def store_cleaned_dataset(self, cleaned_dataset: np.ndarray) -> None:
        DataIO.write_csv(self.cleaned_dataset_path, cleaned_dataset)
