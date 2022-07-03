import multiprocessing
import string
from collections.abc import Iterable
from typing import List

import numpy as np

import backend_library.src.main.backend.task.execution.core.Execution as e
import backend_library.src.main.backend.task.execution.core.ExecutionElement as ee
from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace
from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler


class ExecutionSubspace:
    _cache_subset_lock = multiprocessing.Lock()

    def __init__(self, execution: e.Execution, subspace: Subspace):
        self._execution: e.Execution = execution
        self._subspace: Subspace = subspace

        algorithms: Iterable[ParameterizedAlgorithm] = execution.algorithms

        # further private variables
        self._finished_execution_element_count: int = 0
        self._total_execution_element_count: int = TaskHelper.iterable_length(algorithms)
        self._execution_elements: List[ee.ExecutionElement] = list()

        # shared memory
        self._subspace_shared_memory_name: string = ""

        # initialisation functions
        self.__generate_execution_elements(algorithms)
        self.__schedule_execution_elements()

    def __generate_execution_elements(self, algorithms: Iterable[ParameterizedAlgorithm]) -> None:
        for algorithm in algorithms:
            self._execution_elements.append(ee.ExecutionElement(self, algorithm))

    def __schedule_execution_elements(self) -> None:
        scheduler: Scheduler = Scheduler.get_instance()
        if scheduler is not None:
            for execution_element in self._execution_elements:
                scheduler.schedule(execution_element)

    # getter for ExecutionSubspace
    @property
    def user_id(self) -> int:
        return self._execution.user_id

    @property
    def task_id(self) -> int:
        return self._execution.task_id

    def get_subspace_data_for_processing(self) -> np.ndarray:
        if self._subspace_shared_memory_name is None:
            self.__load_subspace_from_dataset()

        # TODO Tobias: numpy array aus shared_memory ausgeben
        return np.zeros((0, 0))

    def __load_subspace_from_dataset(self) -> np.ndarray:
        self._cache_subset_lock.acquire()
        # TODO Tobias
        self._cache_subset_lock.release()
        return np.zeros((0, 0))

    def execution_element_is_finished(self, error_occurred: bool) -> None:
        self._finished_execution_element_count += 1
        if self._finished_execution_element_count >= self._total_execution_element_count:
            self.__unload_subspace_shared_memory()
        self._execution.on_execution_element_finished(error_occurred)

    def __unload_subspace_shared_memory(self):
        # TODO Tobias
        return None
