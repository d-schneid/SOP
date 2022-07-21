from __future__ import annotations

import json
import multiprocessing
import os
import sys

from multiprocessing import shared_memory
from abc import ABC
from multiprocessing.shared_memory import SharedMemory
from typing import Callable, Optional
from typing import List
from collections.abc import Iterable

import numpy as np

from backend.DataIO import DataIO
from backend.scheduler.Schedulable import Schedulable
from backend.task.Task import Task
from backend.task.TaskState import TaskState
from backend.task.TaskHelper import TaskHelper
from backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend.task.execution.core import ExecutionSubspace
from backend.scheduler.Scheduler import Scheduler
from backend.task.execution.ResultZipper import ResultZipper
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.subspace.Subspace import Subspace


class Execution(Task, Schedulable):
    """
        A task that is provided by the BackendLibrary.
        When scheduled by the Scheduler it executes an execution with the selected cleaned dataset and algorithms.
    """

    def __init__(self, user_id: int, task_id: int,
                 task_progress_callback: Callable[[int, TaskState, float], None],
                 dataset_path: str, result_path: str,
                 subspace_generation: SubspaceGenerationDescription,
                 algorithms: Iterable[ParameterizedAlgorithm],
                 metric_callback: Callable[[Execution], None], datapoint_count: int,
                 final_zip_path: str = "", priority: int = 0):
        """
        :param user_id: The ID of the user belonging to the Execution. Has to be at least -1.
        :param task_id: The ID of the task. Has to be at least -1.
        :param task_progress_callback: The Execution uses this callback to return its progress.
        :param dataset_path: The absolute path to the cleaned dataset which will be used for cleaning.
        (path ends with .csv)
        :param result_path: The absolute path where the Execution will store its results.
        (Ends with the directory name of this specific Execution. f.e. execution1)
        :param final_zip_path: The absolute path where the Execution will store its zipped results.
        :param subspace_generation: Contains all parameters for the subspace generation and will generate the subspaces.
        :param algorithms: Contains all algorithms that should be processed on the subspaces.
        :param metric_callback: Called after the Execution-computation is complete. Carries out the metricizes.
        """
        assert dataset_path.endswith(".csv")
        assert priority >= 0
        assert priority < 5

        Task.__init__(self, user_id, task_id, task_progress_callback)
        self._priority = priority
        self._datapoint_count = datapoint_count

        self._dataset_path: str = dataset_path
        self._result_path: str = result_path
        self._subspace_generation: SubspaceGenerationDescription = subspace_generation
        self._algorithms: list = list(algorithms)
        self._metric_callback: Callable = metric_callback

        # on created logic
        self._execution_element_finished_lock = multiprocessing.Lock()
        self.__fill_algorithms_directory_name()
        self.__generate_file_system_structure()
        self.__generate_execution_details_in_filesystem()
        self._final_zip_path: str = final_zip_path
        if final_zip_path == "":
            self._final_zip_path = result_path + ".zip"

        # The absolute path where the Execution will store its zipped results while doing the zipping.
        self._zip_running_path: str = self._result_path + ".zip.running"

        # further private variables
        self._has_failed_element: bool = False
        self._finished_execution_element_count: int = 0
        self._metric_finished: bool = False

        # generate subspaces
        self._subspaces: List[Subspace] = list(self._subspace_generation.generate())
        self._subspaces_count = len(self._subspaces)
        self._total_execution_element_count: int = self._subspaces_count * len(self._algorithms)

        # generate execution_subspaces
        self._execution_subspaces: List[ExecutionSubspace] = list()

        # shared memory
        self._shared_memory_name: str = TaskHelper.shm_name_generator()
        self._subspace_dtype = np.dtype('f4')

    def __fill_algorithms_directory_name(self) -> None:
        """
        Fills all algorithms with their corresponding directory name in the Execution result folder.  \n
        This is done to allow having multiple algorithms of the same kind in the same Execution.
        Without setting their name individually, algorithms with the same display_name would write their results
        into the same folder, overwriting the results of the other. \n
        :return: None
        """
        algorithm_display_name_dict: dict = {}

        for algorithm in self._algorithms:
            algorithm: ParameterizedAlgorithm = algorithm  # Done to get the type hint
            display_name: str = algorithm.display_name

            if (algorithm_display_name_dict.get(display_name)) is None:
                algorithm.directory_name_in_execution = display_name
                algorithm_display_name_dict[algorithm.display_name] = 1
            else:
                algorithm.directory_name_in_execution = display_name + " (" \
                                                        + str(algorithm_display_name_dict[display_name]) + ")"
                algorithm_display_name_dict[algorithm.display_name] += 1

    # Generates all missing folders of the file system structure of this execution
    def __generate_file_system_structure(self) -> None:
        """
        Creates all necessary directories to store the Execution results. \n
        :return: None
        """
        # if os.path.exists(self.result_path):
        if not os.path.isdir(self._result_path):
            TaskHelper.create_directory(self._result_path)
            for algorithm in self._algorithms:
                algorithm_directory_path: str = os.path.join(self._result_path, algorithm.directory_name_in_execution)
                TaskHelper.create_directory(algorithm_directory_path)

    def __generate_execution_details_in_filesystem(self) -> None:
        """
        Create and store the details.JSON file of the Execution. \n
        It includes information so that the Execution results could be understood and reconstructed.  \n
        :return: None
        """
        assert os.path.isdir(self._result_path)

        details_path: str = os.path.join(self._result_path, 'details.json')

        # create dictionary that will be saved as a JSON-str
        details_dict = {'subspace_generation_information': self._subspace_generation.to_json()}
        for algorithm in self._algorithms:
            algorithm: ParameterizedAlgorithm = algorithm  # To get the type hint
            details_dict[algorithm.directory_name_in_execution] = algorithm.to_json()

        # save JSON-str
        details_json_str: str = json.dumps(details_dict, indent=4)
        with open(details_path, 'w') as f:
            json.dump(details_json_str, f)

    def __generate_execution_subspaces(self) -> None:
        """
        Creates all ExecutionSubspaces that are part of this Execution. \n
        :return: None
        """
        for subspace in self._subspaces:
            self._execution_subspaces.append(
                ExecutionSubspace.
                ExecutionSubspace(self._user_id, self._task_id, self._algorithms,
                                  subspace, self._result_path, self._subspace_dtype,
                                  self.__on_execution_element_finished,
                                  self._shared_memory_name, self._datapoint_count))

    # schedule
    def schedule(self) -> None:
        """
        Inserts the Task into the Scheduler for processing. \n
        :return: None
        """
        if self.__does_zip_exists():
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)
            return

        Scheduler.get_instance().schedule(self)

    def __does_zip_exists(self) -> bool:
        """
        The ZIP-file for the result only exists for finished Executions. So it can be extracted if the Execution
        is finished by checking for the finished ZIP-file. \n
        :return: True if the ZIP-file of the Execution-result exists. Otherwise, return False.
        """
        return os.path.exists(self._final_zip_path)

    def __compute_progress(self) -> float:
        """
        Note: returning float==1 doesn't necessary mean that the Execution is finished. Use TaskState for checking
        if a Task is finished. \n
        :return: A float in [0,1] which indicates the progress of the Execution.
        """
        execution_element_progress: float = float(self._finished_execution_element_count) \
                                            / float(self._total_execution_element_count)
        execution_element_progress *= 0.98  # So all progress is shown (so that the clamping doesn't remove information)
        progress: float = max(0., min(execution_element_progress, 0.98))  # clamp the progress to be more accurate
        if self._metric_finished:
            progress += 0.01
        # Note: The 100% progress is only reached after zipping
        return progress

    def __load_dataset(self) -> None:
        """
        Load the cleaned dataset into shared memory
        """
        data = DataIO.read_cleaned_csv(self._dataset_path)
        size = data.size * data.itemsize
        shm = shared_memory.SharedMemory(self._shared_memory_name, True, size)
        shared_data = np.ndarray(data.shape, data.dtype, shm.buf)
        shared_data[:] = data[:]
        shm.close()

    def __on_execution_element_finished(self, error: bool) -> None:
        """
        The Execution gets notified by the corresponding ExecutionSubspace when an ExecutionElement finished
        by calling this method. \n
        :param error: True if the ExecutionElement finished with an error. Is otherwise False.
        :return: None
        """
        if not self._has_failed_element and error:
            self._has_failed_element = True

        if self._finished_execution_element_count < self._total_execution_element_count:
            with self._execution_element_finished_lock:
                self._finished_execution_element_count += 1
                if self._finished_execution_element_count == self._total_execution_element_count:
                    self.__unload_dataset()
                    self._metric_callback(self)
                    self._metric_finished = True
                    self.__schedule_result_zipping()
        else:
            raise AssertionError("More execution elements finished than existing")

    def __unload_dataset(self) -> None:
        """
        Unloads the cleaned dataset from shared_memory. \n
        :return: None
        """
        assert self._shared_memory_name is not None, \
            "If there is no shared memory currently loaded it can not be unloaded"
        shm = shared_memory.SharedMemory(self._shared_memory_name)
        shm.unlink()
        shm.close()
        self._shared_memory_name = None

    def __schedule_result_zipping(self) -> None:
        """
        Create and schedule the ResultZipping of the Execution into the Scheduler. \n
        :return: None
        """
        result_zipper: ResultZipper = ResultZipper(self._user_id, self._task_id, self._has_failed_element,
                                                   self._task_progress_callback, self._result_path,
                                                   self._zip_running_path, self._final_zip_path)
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(result_zipper)

    # getter for metric
    @property
    def algorithms(self) -> Iterable[ParameterizedAlgorithm]:
        """
        :return: The algorithm information belonging to this Execution.
        """
        return iter(self._algorithms)

    @property
    def subspaces(self) -> Iterable[Subspace]:
        """
        :return: The subspaces belonging to this Execution.
        """
        return iter(self._subspaces)

    @property
    def zip_result_path(self) -> str:
        """
        :return: The absolute path where the ZIP-file of the result of this Execution can be found.
        """
        return self._final_zip_path

    def run_later_on_main(self, statuscode: int):
        self.__generate_execution_subspaces()
        for ess in self._execution_subspaces:
            Scheduler.get_instance().schedule(ess)

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def priority(self) -> int:
        return self._priority

    def do_work(self) -> Optional[int]:
        self.__load_dataset()
