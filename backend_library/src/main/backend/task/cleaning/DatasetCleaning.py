import os
import string
from collections.abc import Callable, Iterable
from typing import Optional

import numpy as np

from CategoricalColumnRemover import CategoricalColumnRemover
from ImputationMode import ImputationMode
from MinMaxScaler import MinMaxScaler
from backend_library.src.main.backend.DataIO import DataIO
from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler
from backend_library.src.main.backend.scheduler.Schedulable import Schedulable
from DatasetCleaningStep import DatasetCleaningStep


class DatasetCleaning(Task, Schedulable):

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable[[int, TaskState, float], None],
                 original_dataset_path: string, cleaned_dataset_path: string,
                 cleaning_steps: Iterable[DatasetCleaningStep] = None):
        Task.__init__(self, user_id, task_id, task_progress_callback)
        if cleaning_steps is None:
            cleaning_steps = [CategoricalColumnRemover(), ImputationMode(), MinMaxScaler()]  # Default Cleaning-Pipeline
        self._original_dataset_path: string = original_dataset_path
        self._cleaned_dataset_path: string = cleaned_dataset_path
        self._cleaning_steps: Iterable[DatasetCleaningStep] = cleaning_steps
        self._cleaning_steps_count: int = TaskHelper.iterable_length(self._cleaning_steps)

    def schedule(self) -> None:
        if self.__did_cleaning_finish():
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)
            return None
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(DatasetCleaning)

    def __did_cleaning_finish(self) -> bool:
        return os.path.isfile(self._cleaned_dataset_path)

    # scheduling #############################################
    def get_user_id(self) -> int:
        return self._user_id

    def get_task_id(self) -> int:
        return self._task_id

    def do_work(self) -> None:
        self.__delete_old_error_file()

        dataset_to_clean: np.ndarray = self.__load_original_dataset()
        cleaning_pipeline_result: Optional[np.ndarray] = self.__run_cleaning_pipeline(dataset_to_clean)

        if cleaning_pipeline_result is None:  # cleaning failed
            self._task_progress_callback(self._task_id, TaskState.FINISHED_WITH_ERROR, 1.0)
            return

        cleaned_dataset: np.ndarray = cleaning_pipeline_result.astype(
            np.float32)  # cast ndarray to float32 # TODO: Vllt copy=False

        if TaskHelper.is_float_csv(cleaned_dataset):
            self.__store_cleaned_dataset(cleaned_dataset)
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)
        else:
            error_message: string = "Error: Type != float32 in cleaned_file"
            TaskHelper.save_error_csv(self._cleaned_dataset_path, error_message)
            self._task_progress_callback(self._task_id, TaskState.FINISHED_WITH_ERROR, 1.0)

    # do_work #############################################
    def __delete_old_error_file(self) -> None:
        error_file_path: string = TaskHelper.convert_to_error_csv_path(self._cleaned_dataset_path)
        if os.path.isfile(error_file_path):
            os.remove(error_file_path)

    def __load_original_dataset(self) -> np.ndarray:
        return DataIO.read_uncleaned_csv(self._original_dataset_path)

    def __run_cleaning_pipeline(self, csv_to_clean) -> Optional[np.ndarray]:
        finished_cleaning_steps: int = 0

        for cleaning_step in self._cleaning_steps:
            try:
                if cleaning_step is not None:
                    csv_to_clean = cleaning_step.do_cleaning(csv_to_clean)
            except Exception as e:  # catch *all* exceptions
                TaskHelper.save_error_csv(self._cleaned_dataset_path, str(e))
                return None

            finished_cleaning_steps += 1
            progress: float = min(finished_cleaning_steps / self._cleaning_steps_count,
                                  0.99)  # compute and clamp progress
            self._task_progress_callback(self._task_id, TaskState.RUNNING, progress)

    def __store_cleaned_dataset(self, cleaned_dataset: np.ndarray) -> None:
        DataIO.write_csv(self._cleaned_dataset_path, cleaned_dataset)
