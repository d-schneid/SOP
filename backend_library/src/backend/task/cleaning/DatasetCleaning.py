import os
from abc import ABC
from collections.abc import Callable
from typing import Optional

import numpy as np

from backend.AnnotatedDataset import AnnotatedDataset
from backend.DataIO import DataIO
from backend.task.Task import Task
from backend.task.TaskHelper import TaskHelper
from backend.task.TaskState import TaskState
from backend.scheduler.Scheduler import Scheduler
from backend.scheduler.Schedulable import Schedulable
from backend.task.cleaning.DatasetCleaningStep import DatasetCleaningStep
from backend.task.cleaning.CategoricalColumnRemover import CategoricalColumnRemover
from backend.task.cleaning.ImputationMode import ImputationMode
from backend.task.cleaning.MinMaxScaler import MinMaxScaler
from backend.task.cleaning.RowOrColumnMissingValuesRemover \
    import RowOrColumnMissingValuesRemover as none_roc_remover
from backend.task.TaskErrorMessages import TaskErrorMessages


class DatasetCleaning(Task, Schedulable, ABC):
    """
    A task that is provided by the BackendLibrary.
    When scheduled by the Scheduler it cleans a dataset and
    stores the cleaned dataset separately in cleaned_dataset_path.
    """

    def __init__(self, user_id: int, task_id: int,
                 task_progress_callback: Callable[[int, TaskState, float], None],
                 uncleaned_dataset_path: str, cleaned_dataset_path: str,
                 cleaning_steps: Optional[list[DatasetCleaningStep]] = None,
                 priority: int = 100,
                 running_dataset_cleaning_path: str = ""):
        """
        :param user_id: The ID of the user belonging to the DatasetCleaning.
        Has to be at least -1.
        :param task_id: The ID of the task. Has to be at least -1.
        :param task_progress_callback: The DatasetCleaning uses this callback
        to return its progress.
        :param uncleaned_dataset_path: The absolute path where the DatasetCleaning
        can find the uncleaned dataset which will be cleaned.
        (The path contains the dataset name and ends with .csv)
        :param cleaned_dataset_path: The absolute path where the DatasetCleaning will
        store the cleaned dataset.
        (The path contains the dataset name and ends with .csv)
        :param cleaning_steps: Specifies the cleaning pipeline that will be used
        for cleaning. If None is inputted the
        default cleaning pipeline is used.
        :param priority: The priority of the task for the Scheduling.
        :param running_dataset_cleaning_path: The path where the DatasetCleaning
        writes it temporary results to.
        If "" was inputted it writes the temporary result relatively to the
        uncleaned_dataset_path.
        """
        Task.__init__(self, user_id, task_id, task_progress_callback)
        if cleaning_steps is None:
            cleaning_steps = [CategoricalColumnRemover(), none_roc_remover(1),
                              none_roc_remover(0),
                              ImputationMode(),
                              MinMaxScaler()]  # Default Cleaning-Pipeline
        assert all(step is not None for step in cleaning_steps)
        self._uncleaned_dataset_path: str = uncleaned_dataset_path
        self._cleaned_dataset_path: str = cleaned_dataset_path
        self._cleaning_steps: list[DatasetCleaningStep] = cleaning_steps
        self._cleaning_steps_count: int = len(self._cleaning_steps)
        self._priority = priority
        if running_dataset_cleaning_path == "":
            self._running_dataset_cleaning_path = uncleaned_dataset_path + ".running"
        else:
            self._running_dataset_cleaning_path = running_dataset_cleaning_path

    def schedule(self) -> None:
        """
        Inserts the Task into the Scheduler for processing. \n
        :return: None
        """
        if self.__did_cleaning_finish():
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)
            return None
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(self)

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
        return self._priority

    def do_work(self) -> None:
        """
        Is called by the scheduler to do the dataset cleaning. \n
        :return: None
        """
        self.__delete_old_error_file()

        dataset_to_clean: AnnotatedDataset = self.__load_uncleaned_dataset()

        cleaning_pipeline_result: Optional[
            AnnotatedDataset] = self.__run_cleaning_pipeline(dataset_to_clean)

        if cleaning_pipeline_result is None:  # cleaning failed
            self._task_progress_callback(self._task_id, TaskState.FINISHED_WITH_ERROR,
                                         1.0)
            return

        # Casting will throw an exception
        # if the cleaned dataset cannot be converted to only float32 values
        try:
            cleaning_pipeline_result.data = cleaning_pipeline_result.data.astype(
                np.float32, copy=False)  # cast ndarray to float32
        except ValueError as e:
            TaskHelper.save_error_csv(self._cleaned_dataset_path,
                                      TaskErrorMessages().cast_to_float32_error + str(
                                          e))
            self._task_progress_callback(self._task_id, TaskState.FINISHED_WITH_ERROR,
                                         1.0)
            return

        # store cleaned dataset in path
        data = cleaning_pipeline_result.to_single_array()
        DataIO.save_write_csv(self._running_dataset_cleaning_path,
                              self._cleaned_dataset_path, data, add_index_column=False)

        # report webserver the task progress
        self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)

    # do_work helper #############################################
    def __delete_old_error_file(self) -> None:
        """
        If there exists an old error file belonging to this DatasetCleaning,
        it will be deleted. \n
        :return: None
        """
        error_file_path: str = TaskHelper.convert_to_error_csv_path(
            self._cleaned_dataset_path)
        if os.path.isfile(error_file_path):
            os.remove(error_file_path)

    def __load_uncleaned_dataset(self) -> AnnotatedDataset:
        """ Loads the uncleaned dataset which will be cleaned. \n
        :return: The loaded uncleaned dataset.
        (Throws FileNotFoundError if there exists no file at the uncleaned_dataset_path)
        """
        return DataIO.read_annotated(self._uncleaned_dataset_path, is_cleaned=False,
                                     has_row_numbers=False)

    def __run_cleaning_pipeline(self, csv_to_clean: AnnotatedDataset) -> \
            Optional[AnnotatedDataset]:
        """
        Runs each DatasetToClean of the cleaning_pipline
        on the uncleaned dataset sequentially. \n
        :param csv_to_clean: The dataset that should be cleaned.
        :return: None if the cleaning failed. Otherwise, returns the cleaned dataset.
        """
        if self.__empty_cleaning_result_handler(csv_to_clean.data):  # csv is empty
            return None

        finished_cleaning_steps: int = 0

        for cleaning_step in self._cleaning_steps:
            try:
                csv_to_clean = cleaning_step.do_cleaning(csv_to_clean)
            except Exception as e:  # catch all exceptions
                if str(e) == "":
                    e = "Error: " + str(cleaning_step) + " resulted in an error"
                TaskHelper.save_error_csv(self._cleaned_dataset_path, str(e))
                return None

            # Exception handling
            if self.__empty_cleaning_result_handler(csv_to_clean.data):  # csv is empty
                return None

            # Progress handling
            finished_cleaning_steps += 1
            progress: float = min(
                float(finished_cleaning_steps) / float(self._cleaning_steps_count),
                0.99)  # compute and clamp progress
            self._task_progress_callback(self._task_id, TaskState.RUNNING, progress)

        return csv_to_clean

    def __empty_cleaning_result_handler(self, csv_to_check: np.ndarray) -> bool:
        """
        Checks if the cleaning result is empty. If this is the case create
        and store the error file and return True.
        :param csv_to_check: The array that should be checked.
        :return: True, if the array is empty. Otherwise, return False.
        """
        if csv_to_check.size == 0:
            error: str = TaskErrorMessages().cleaning_result_empty
            TaskHelper.save_error_csv(self._cleaned_dataset_path, str(error))
            return True
        return False

    def __str__(self):
        return f"DatasetCleaning {self.task_id} from user {self.user_id}" \
            f"cleans dataset from {self._uncleaned_dataset_path}" \
            f"to {self._cleaned_dataset_path}"
