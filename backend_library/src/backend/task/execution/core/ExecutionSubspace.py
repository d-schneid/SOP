from __future__ import annotations

import multiprocessing
import os

import sys
from collections.abc import Iterable
from typing import List

import numpy as np

from backend.task.execution.core import ExecutionElement
from backend.task.execution.core import Execution
from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.TaskHelper import TaskHelper
from backend.scheduler.Scheduler import Scheduler


class ExecutionSubspace:
    """
    Manages the computations of all algorithms of an Execution, that compute their results on the same Subspace.
    """
    _cache_subset_lock = multiprocessing.Lock()

    def __init__(self, execution: Execution, subspace: Subspace):
        """
        :param execution: The Execution this ExecutionSubspace belongs to.
        :param subspace: The Subspace whose ExecutionElements are managed by this ExecutionSubspace.
        """
        self._execution: Execution = execution
        self._subspace: Subspace = subspace

        algorithms: Iterable[ParameterizedAlgorithm] = execution.algorithms

        # further private variables
        self._finished_execution_element_count: int = 0
        self._total_execution_element_count: int = TaskHelper.iterable_length(algorithms)
        self._execution_elements: List[ExecutionElement] = list()

        # shared memory
        self._subspace_shared_memory_name: str = ""

        # initialisation functions
        self.__generate_execution_elements(algorithms)
        self.__schedule_execution_elements()

    def __generate_execution_elements(self, algorithms: Iterable[ParameterizedAlgorithm]) -> None:
        """
        :param algorithms: All algorithms that are selected for the Execution.
        :return: None
        """
        for algorithm in algorithms:
            result_path: str = os.path.join(self._execution.zip_result_path,
                                            algorithm.directory_name_in_execution)  # TODO: TEST THIS!
            self._execution_elements.append(ExecutionElement.ExecutionElement(self, algorithm, result_path))

    def __schedule_execution_elements(self) -> None:
        """
        Insert all ExecutionElements of this ExecutionSubspace into the Scheduler. \n
        :return: None
        """
        scheduler: Scheduler = Scheduler.get_instance()
        for execution_element in self._execution_elements:
            scheduler.schedule(execution_element)

    # getter for ExecutionSubspace
    @property
    def user_id(self) -> int:
        """
        :return: The ID of the user belonging to this Execution.
        """
        return self._execution.user_id

    @property
    def task_id(self) -> int:
        """
        :return: The ID of the task.
        """
        return self._execution.task_id

    def get_subspace_data_for_processing(self) -> np.ndarray:
        """
        Returns the dataset for this subset from shared_memory. \n
        :return: The subspace_dataset (from shared_memory).
        """
        if self._subspace_shared_memory_name is None:
            self.__load_subspace_from_dataset()

        # TODO Tobias: numpy array aus shared_memory ausgeben
        return np.zeros((0, 0))

    def __load_subspace_from_dataset(self) -> np.ndarray:
        """
        :return: Loads the dataset for this subspace into shared_memory, if it isn't loaded into the shared_memory yet.
        """
        self._cache_subset_lock.acquire()
        # TODO Tobias
        self._cache_subset_lock.release()
        return np.zeros((0, 0))

    def execution_element_is_finished(self, error_occurred: bool) -> None:
        """
        The ExecutionSubspace gets notified by an ExecutionElement when it finishes by calling this method. \n
        Passes the notification on to the Execution. \n
        :param error_occurred: True if the ExecutionElement finished with an error. Is otherwise False.
        :return: None
        """
        self._finished_execution_element_count += 1
        if self._finished_execution_element_count >= self._total_execution_element_count:
            self.__unload_subspace_shared_memory()
        self._execution.on_execution_element_finished(error_occurred)

    def __unload_subspace_shared_memory(self) -> None:
        """
        Unlinks the dataset from the subspace from shared_memory. \n
        :return: None
        """
        # TODO Tobias
        return None
