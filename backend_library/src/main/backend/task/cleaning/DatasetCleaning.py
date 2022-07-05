import os
from abc import ABC
from collections.abc import Callable, Iterable
from typing import Optional

import numpy as np

from backend_library.src.main.backend.DataIO import DataIO
from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler
from backend_library.src.main.backend.scheduler.Schedulable import Schedulable
from DatasetCleaningStep import DatasetCleaningStep
from CategoricalColumnRemover import CategoricalColumnRemover
from ImputationMode import ImputationMode
from MinMaxScaler import MinMaxScaler
from RowThresholdMissingValuesRemover import RowThresholdMissingValuesRemover


class DatasetCleaning(Task, Schedulable, ABC):
    """
    A task that is provided by the BackendLibrary.
    When scheduled by the Scheduler it cleans a dataset and
    stores the cleaned dataset separately in cleaned_dataset_path.
    """
    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable[[int, TaskState, float], None],
                 original_dataset_path: str, cleaned_dataset_path: str,
                 cleaning_steps: Iterable[DatasetCleaningStep] = None):
        """
        :param user_id: The ID of the user belonging to the DatasetCleaning.
        :param task_id: The ID of the task.
        :param task_progress_callback: The DatasetCleaning uses this callback to return its progress.
        :param original_dataset_path: The absolute path where the DatasetCleaning can find the uncleaned dataset
        which will be cleaned. (The path contains the dataset name and ends with .csv)
        :param cleaned_dataset_path: The absolute path where the DatasetCleaning will store the cleaned dataset.
        (The path contains the dataset name and ends with .csv)
        :param cleaning_steps: Specifies the cleaning pipeline that will be used for cleaning. If None is inputted the
        default cleaning pipeline is used.
        """
        Task.__init__(self, user_id, task_id, task_progress_callback)
        if cleaning_steps is None:
            cleaning_steps = [RowThresholdMissingValuesRemover(), CategoricalColumnRemover(),
                              ImputationMode(), MinMaxScaler()]  # Default Cleaning-Pipeline
        self._original_dataset_path: str = original_dataset_path
        self._cleaned_dataset_path: str = cleaned_dataset_path
        self._cleaning_steps: Iterable[DatasetCleaningStep] = cleaning_steps
        self._cleaning_steps_count: int = TaskHelper.iterable_length(self._cleaning_steps)

    def schedule(self) -> None:
        """
        Inserts the Task into the Scheduler for processing. \n
        :return: None
        """
        if self.__did_cleaning_finish():
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)
            return None
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(DatasetCleaning)

    def __did_cleaning_finish(self) -> bool:
        """
        :return: True if the cleaning already finished otherwise returns False.
        """
        return os.path.isfile(self._cleaned_dataset_path)

    # scheduling #############################################
    @property
    def user_id(self) -> int:
        """
        :return: The ID of the user belonging to this DatasetCleaning.
        """
        return self._user_id

    @property
    def task_id(self) -> int:
        """
        :return: The ID of the task.
        """
        return self._task_id

    @property
    def priority(self) -> int:
        """
        :return: The priority for the Scheduler.
        """
        return 100

    def do_work(self) -> None:
        """
        Is called by the scheduler to do the dataset cleaning. \n
        :return: None
        """
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
            error_message: str = "Error: Type != float32 in cleaned_file"
            TaskHelper.save_error_csv(self._cleaned_dataset_path, error_message)
            self._task_progress_callback(self._task_id, TaskState.FINISHED_WITH_ERROR, 1.0)

    # do_work #############################################
    def __delete_old_error_file(self) -> None:
        """
        If there exists an old error file belonging to this DatasetCleaning, it will be deleted. \n
        :return: None
        """
        error_file_path: str = TaskHelper.convert_to_error_csv_path(self._cleaned_dataset_path)
        if os.path.isfile(error_file_path):
            os.remove(error_file_path)

    def __load_original_dataset(self) -> np.ndarray:
        """ Loads the uncleaned dataset which will be cleaned. \n
        :return: The loaded uncleaned dataset.
        """
        return DataIO.read_uncleaned_csv(self._original_dataset_path)

    def __run_cleaning_pipeline(self, csv_to_clean: np.ndarray) -> Optional[np.ndarray]:
        """
        Runs each DatasetToClean of the cleaning_pipline on the uncleaned dataset sequentially. \n
        :param csv_to_clean: The dataset that should be cleaned.
        :return: None if the cleaning failed. Otherwise, returns the cleaned dataset.
        """
        if self.__empty_cleaning_result_handler(csv_to_clean):  # csv is empty
            return None

        finished_cleaning_steps: int = 0

        for cleaning_step in self._cleaning_steps:
            try:
                if cleaning_step is not None:
                    csv_to_clean = cleaning_step.do_cleaning(csv_to_clean)
            except Exception as e:  # catch all exceptions
                TaskHelper.save_error_csv(self._cleaned_dataset_path, str(e))
                return None
            if self.__empty_cleaning_result_handler(csv_to_clean):  # csv is empty
                return None
            finished_cleaning_steps += 1
            progress: float = min(finished_cleaning_steps / self._cleaning_steps_count,
                                  0.99)  # compute and clamp progress
            self._task_progress_callback(self._task_id, TaskState.RUNNING, progress)

    def __store_cleaned_dataset(self, cleaned_dataset: np.ndarray) -> None:
        """ Stores the cleaned dataset in the FileStorage. \n
        :param cleaned_dataset: Dataset that should be stored
        :return: None
        """
        DataIO.write_csv(self._cleaned_dataset_path, cleaned_dataset)

    def __empty_cleaning_result_handler(self, csv_to_check: np.ndarray) -> bool:
        """
        Checks if the cleaning result is empty. If this is the case create and store the error file and return True.
        :param csv_to_check: The array that should be checked.
        :return: True, if the array is empty. Otherwise, return False.
        """
        if csv_to_check.shape[0] == 0 or csv_to_check.shape[1] == 0:
            error: str = "Cleaning resulted in empty dataset"
            TaskHelper.save_error_csv(self._cleaned_dataset_path, str(error))
            return True
        return False
