from __future__ import annotations

import multiprocessing
import os
from collections.abc import Iterable
from multiprocessing.shared_memory import SharedMemory
from typing import Callable
from typing import List, Optional

import numpy as np

from backend.scheduler.Schedulable import Schedulable
from backend.scheduler.Scheduler import Scheduler
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core import ExecutionElement
from backend.task.execution.subspace.Subspace import Subspace


class ExecutionSubspace(Schedulable):
    """
    Manages the computations of all algorithms of an Execution, that compute their results on the same Subspace.
    """

    def __init__(self, user_id: int, task_id: int,
                 algorithms: Iterable[ParameterizedAlgorithm], subspace: Subspace,
                 result_path: str, ds_on_main: np.ndarray,
                 on_execution_element_finished_callback: Callable[[bool], None],
                 ds_shm_name: str, priority: int = 5):
        """
        :param ds_shm_name: name of the shared emory segment containing the full dataset
        :param user_id: The ID of the user belonging to the ExecutionSubspace. Has to be at least -1.
        :param task_id: The ID of the task. Has to be at least -1.
        :param algorithms: Contains all algorithms that should be processed on the subspaces.
        :param subspace: The Subspace whose ExecutionElements are managed by this ExecutionSubspace.
        :param _result_path: The absolute path where the Execution will store its results
        (ends with the directory name of this specific Execution. f.e. execution1).
        :param ds_on_main: The dtype of the values that are stored in the dataset for processing
        :param on_execution_element_finished_callback: Reports the Execution that a ExecutionElement finished.
        """
        assert priority < 10
        assert priority >= 5

        assert user_id >= -1
        assert task_id >= -1

        # privates from Constructor
        self._ds_shm_name: str = ds_shm_name
        self._user_id: int = user_id
        self._task_id: int = task_id
        self._subspace: Subspace = subspace
        self._algorithms: list[ParameterizedAlgorithm] = list(algorithms)
        self._result_path: str = result_path
        self._ds_on_main: np.ndarray = ds_on_main
        self._on_execution_element_finished_callback: Callable[[bool], None] = \
            on_execution_element_finished_callback
        self._priority = priority

        # further private variables
        self._finished_execution_element_count: int = 0
        self._total_execution_element_count: int = len(self._algorithms)
        self._execution_elements: List[ExecutionElement] = list()

        # shared memory
        self._subspace_shared_memory_name: Optional[str] = None
        self._subspace_shared_memory_on_main: Optional[SharedMemory] = None

        # lock for multiprocessing
        self._cache_subset_lock = multiprocessing.Lock()
        self._algorithms = algorithms

    def __generate_execution_elements(self, algorithms: Iterable[ParameterizedAlgorithm]) -> None:
        """
        :param algorithms: All algorithms that are selected for the Execution.
        :return: None
        """
        for algorithm in algorithms:
            result_path: str = os.path.join(
                os.path.join(self._result_path,
                             algorithm.directory_name_in_execution),
                self._subspace.get_subspace_identifier() + ".csv")  # TODO: TEST THIS!

            self._execution_elements.append(
                ExecutionElement.ExecutionElement(self._user_id, self._task_id,
                                                  self._subspace, algorithm,
                                                  result_path, self._ds_on_main.dtype,
                                                  self._subspace_shared_memory_name,
                                                  self.__execution_element_is_finished,
                                                  self._ds_on_main.shape[0]))

    def __schedule_execution_elements(self) -> None:
        """
        Insert all ExecutionElements of this ExecutionSubspace into the Scheduler. \n
        :return: None
        """
        scheduler: Scheduler = Scheduler.get_instance()
        for execution_element in self._execution_elements:
            scheduler.schedule(execution_element)

    def __load_subspace_from_dataset(self) -> SharedMemory:
        """
        :return: Loads the dataset for this subspace into shared_memory
        """
        ds_shm: SharedMemory = SharedMemory(self._ds_shm_name)
        ds_dim_cnt: int = self._subspace.get_dataset_dimension_count()
        ds_arr = np.ndarray((self._ds_on_main.shape[0], ds_dim_cnt),
                            dtype=self._ds_on_main.dtype, buffer=ds_shm.buf)
        buffer_size = self._subspace.get_size_of_subspace_buffer(ds_arr)
        ss_shm = SharedMemory(self._subspace_shared_memory_name, False)
        self._subspace.make_subspace_array(ds_arr, ss_shm)
        return ss_shm

    def __execution_element_is_finished(self, error_occurred: bool) -> None:
        """
        The ExecutionSubspace gets notified by an ExecutionElement when it finishes by calling this method. \n
        Passes the notification on to the Execution. \n
        :param error_occurred: True if the ExecutionElement finished with an error. Is otherwise False.
        :return: None
        """
        if self._finished_execution_element_count < self._total_execution_element_count:
            self._finished_execution_element_count += 1
            if self._finished_execution_element_count >= self._total_execution_element_count:
                self.__unload_subspace_shared_memory()
        else:
            raise AssertionError("More execution elements finished than existing")
        self._on_execution_element_finished_callback(error_occurred)

    def __unload_subspace_shared_memory(self) -> None:
        """
        Unlinks the dataset from the subspace from shared_memory. \n
        :return: None
        """
        assert self._subspace_shared_memory_name is not None
        self._subspace_shared_memory_on_main.unlink()
        self._subspace_shared_memory_on_main.close()
        self._subspace_shared_memory_name = None

    def run_later_on_main(self, statuscode: int) -> None:
        self.__generate_execution_elements(self._algorithms)
        for ee in self._execution_elements:
            Scheduler.get_instance().schedule(ee)

    def run_before_on_main(self) -> None:
        size = self._subspace.get_size_of_subspace_buffer(self._ds_on_main)
        self._subspace_shared_memory_on_main = SharedMemory(None, True, size)
        self._subspace_shared_memory_name = self._subspace_shared_memory_on_main.name

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def priority(self) -> int:
        return self._priority

    def do_work(self) -> None:
        self.__load_subspace_from_dataset()
