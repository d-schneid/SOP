from __future__ import annotations

import json
import multiprocessing
import os

from abc import ABC
from typing import Callable, Optional
from typing import List
from collections.abc import Iterable

import pandas as pd

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend_library.src.main.backend.task.execution.core.ExecutionSubspace import ExecutionSubspace
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler
from backend_library.src.main.backend.task.execution.ResultZipper import ResultZipper
from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace


class Execution(Task, ABC):
    """
        A task that is provided by the BackendLibrary.
        When scheduled by the Scheduler it executes an execution with the selected cleaned dataset and algorithms.
    """
    _cache_dataset_lock = multiprocessing.Lock()
    _execution_element_finished_lock = multiprocessing.Lock()

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable[[int, TaskState, float], None],
                 dataset_path: str, result_path: str, subspace_generation: SubspaceGenerationDescription,
                 algorithms: Iterable[ParameterizedAlgorithm], metric_callback: Callable[[Execution], None],
                 data_dimensions_count: int):
        """
        :param user_id: The ID of the user belonging to the Execution. Has to be at least -1.
        :param task_id: The ID of the task. Has to be at least -1.
        :param task_progress_callback: The Execution uses this callback to return its progress.
        :param dataset_path: The absolute path to the cleaned dataset which will be used for cleaning.
        (path ends with .csv)
        :param result_path: The absolute path where the Execution will store its results.
        (Ends with the directory name of this specific Execution. f.e. execution1)
        :param subspace_generation: Contains all parameters for the subspace generation and will generate the subspaces.
        :param algorithms: Contains all algorithms that should be processed on the subspaces.
        :param metric_callback: Called after the Execution-computation is complete. Carries out the metricizes.
        """
        Task.__init__(self, user_id, task_id, task_progress_callback)
        self._dataset_path: str = dataset_path
        self._result_path: str = result_path
        self._subspace_generation: SubspaceGenerationDescription = subspace_generation
        self._algorithms: Iterable[ParameterizedAlgorithm] = algorithms
        self._metric_callback: Callable = metric_callback

        # on created logic
        self.__fill_algorithms_directory_name()
        self.__generate_file_system_structure()
        self._zipped_result_path: str = self._result_path + ".zip"

        # further private variables
        self._has_failed_element: bool = False
        self._finished_execution_element_count: int = 0
        self._metric_finished: bool = False

        # generate subspaces
        self._subspaces: Iterable[Subspace] = self._subspace_generation.generate(data_dimensions_count)
        self._subspaces_count = TaskHelper.iterable_length(self._subspaces)
        self._total_execution_element_count: int = self._subspaces_count * TaskHelper.iterable_length(algorithms)

        # generate execution_subspaces
        self._execution_subspaces: List[ExecutionSubspace] = list()
        self.__generate_execution_subspaces()

        # shared memory
        self._shared_memory_name: str = ""

    def __fill_algorithms_directory_name(self) -> None:
        """
        Fills all algorithms with their corresponding directory name in the Execution result folder.  \n
        This is done to allow having multiple algorithms of the same kind in the same Execution.
        Without setting their name individually, algorithms with the same display_name would write their results
        into the same folder, overwriting the results of the other.  \n
        :return: None
        """
        algorithm_display_name_dict: dict = {}

        for algorithm in self._algorithms:
            algorithm: ParameterizedAlgorithm = algorithm  # Done to get the type hint
            display_name: str = algorithm.display_name

            if (algorithm_display_name_dict.get(display_name)) is None:
                algorithm.directory_name_in_execution = display_name
                algorithm_display_name_dict[algorithm.directory_name_in_execution] = 0
            else:
                algorithm.directory_name_in_execution = display_name + " (" \
                                                        + algorithm_display_name_dict[display_name] + ")"
                algorithm_display_name_dict[algorithm.directory_name_in_execution] += 1

    # Generates all missing folders of the file system structure of this execution
    def __generate_file_system_structure(self) -> None:
        """
        Creates all necessary directories to store the Execution results. \n
        :return: None
        """
        # if os.path.exists(self.result_path):
        if os.path.isdir(self._result_path):
            TaskHelper.create_directory(self._result_path)
            for algorithm in self._algorithms:
                algorithm_directory_path: str = self._result_path + '\\' + algorithm.display_name
                TaskHelper.create_directory(algorithm_directory_path)

    def __generate_execution_details_in_filesystem(self) -> None:
        """
        Create and store the details.JSON file of the Execution. \n
        It includes information so that the Execution results could be understood and reconstructed.  \n
        :return: None
        """
        details_path: str = self._result_path + 'details.json'

        # create dictionary that will be saved as a JSON-str
        details_dict = {'subspace_generation_information': self._subspace_generation.to_json()}
        for algorithm in self._algorithms:
            algorithm: ParameterizedAlgorithm = algorithm  # To get the type hint
            details_dict[algorithm.directory_name_in_execution] += algorithm.to_json()

        # save JSON-str
        details_json_str: str = json.dumps(details_dict, indent=4)
        with open(details_path, 'w') as f:  # TODO: Test if this is correct
            json.dump(details_json_str, f)

    def __generate_execution_subspaces(self) -> None:
        """
        Creates all ExecutionSubspaces that are part of this Execution. \n
        :return: None
        """
        for subspace in self._subspaces:
            self._execution_subspaces.append(ExecutionSubspace.ExecutionSubspace(self, subspace))

    # schedule
    def schedule(self) -> None:
        """
        Inserts the Task into the Scheduler for processing. \n
        :return: None
        """
        if self.__does_zip_exists():
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)
            return
        scheduler: Scheduler = Scheduler.get_instance()
        # you can not schedule something that is not schedulable
        # scheduler.schedule(Execution)

    def __does_zip_exists(self) -> bool:
        """
        The ZIP-file for the result only exists for finished Executions. So it can be extracted if the Execution
        is finished by checking for the finished ZIP-file. \n
        :return: True if the ZIP-file of the Execution-result exists. Otherwise, return False.
        """
        return os.path.exists(self._zipped_result_path)

    def __compute_progress(self) -> float:
        """
        Note: returning float==1 doesn't necessary mean that the Execution is finished. Use TaskState for checking
        if a Task is finished. \n
        :return: A float in [0,1] which indicates the progress of the Execution.
        """
        execution_element_progress: float = self._finished_execution_element_count / self._total_execution_element_count
        progress: float = max(execution_element_progress, 0.98)  # clamp the progress to be more accurate
        if self._metric_finished:
            progress += 0.01
        # Note: The 100% progress is only reached after zipping
        return progress

    # getter for ExecutionSubspace
    @property
    def user_id(self) -> int:
        """
        :return: The ID of the user belonging to this Execution.
        """
        return self._user_id

    @property
    def task_id(self) -> int:
        """
        :return: The ID of the task.
        """
        return self._task_id

    @property
    def result_path(self) -> str:
        """
        :return: The absolute path where the Execution result-directory is stored.
        """
        return self._result_path

    def cache_dataset(self) -> str:
        """
        Load the cleaned dataset, if it isn't loaded into the shared memory yet. \n
        :return: The shared_memory_name of the cleaned dataset.
        """
        Execution._cache_dataset_lock.acquire()
        # TODO: Tobias
        Execution._cache_dataset_lock.release()
        pass

    def on_execution_element_finished(self, error: bool) -> None:
        """
        The Execution gets notified by the corresponding ExecutionSubspace when an ExecutionElement finished
        by calling this method. \n
        :param error: True if the ExecutionElement finished with an error. Is otherwise False.
        :return: None
        """
        if not self._has_failed_element and error:
            self._has_failed_element = True

        Execution._execution_element_finished_lock.acquire()
        self._finished_execution_element_count += 1
        if self._finished_execution_element_count == self._total_execution_element_count:
            self.__unload_dataset()
            self._metric_callback(self)
            self._metric_finished = True
            self.__schedule_result_zipping()
        Execution._execution_element_finished_lock.release()

    def __unload_dataset(self) -> None:
        """
        Unloads the cleaned dataset from shared_memory. \n
        :return: None
        """
        # TODO: Tobias
        self._shared_memory_name = ""
        pass

    def __schedule_result_zipping(self) -> None:
        """
        Create and schedule the ResultZipping of the Execution into the Scheduler. \n
        :return: None
        """
        result_zipper: ResultZipper = ResultZipper(self._user_id, self._task_id, self._has_failed_element,
                                                   self._task_progress_callback, self._result_path,
                                                   self._zipped_result_path)
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(result_zipper)

    # getter for metric
    @property
    def algorithms(self) -> Iterable[ParameterizedAlgorithm]:
        """
        :return: The algorithm information belonging to this Execution.
        """
        return self._algorithms

    @property
    def subspaces(self) -> Iterable[Subspace]:
        """
        :return: The subspaces belonging to this Execution.
        """
        return self._subspaces

    @property
    def zip_result_path(self) -> str:
        """
        :return: The absolute path where the ZIP-file of the result of this Execution can be found.
        """
        return self._zipped_result_path
