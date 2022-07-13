from __future__ import annotations

import os

from abc import ABC

import numpy as np

from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.scheduler.Schedulable import Schedulable
from backend.DataIO import DataIO
from typing import Callable
from multiprocessing.shared_memory import SharedMemory
from backend.task.execution.subspace.Subspace import Subspace


class ExecutionElement(Schedulable, ABC):
    """
    Is the smallest unit of an Execution.
    Consists of the computation of one algorithm on exactly one subspace.
    """
    def __init__(self, user_id: int, task_id: int, subspace: Subspace, algorithm: ParameterizedAlgorithm,
                 result_path: str, subspace_dtype: np.dtype,
                 get_subspace_data_for_processing: Callable[[], SharedMemory],
                 execution_element_is_finished: Callable[[bool], None], priority: int = 0):
        """
        :param user_id: The ID of the user belonging to this ExecutionElement. Has to be at least -1.
        :param task_id: The ID of this task. Has to be at least -1.
        :param subspace: The subspace on which the algorithm should compute its result.
        :param algorithm: The algorithm that should be computed on the subspace.
        :param result_path: The directory where the result-csv-file of the ExecutionElement-computation will be stored.
        :param subspace_dtype: The dtype of the values that are stored in the dataset for processing.
        :param get_subspace_data_for_processing: Gets the subspace dataset where the ExecutionElement can
        compute its result.
        :param execution_element_is_finished: Reports the ExecutionSubspace that it finished its execution.
        :param priority: The priority of this Schedulable for the Scheduler.
        """
        assert user_id >= -1
        assert task_id >= -1

        self._user_id: int = user_id
        self._task_id: int = task_id
        self._priority: int = priority

        self._subspace: Subspace = subspace
        self._algorithm: ParameterizedAlgorithm = algorithm

        self._result_path: str = result_path
        self._subspace_dtype: np.dtype = subspace_dtype

        self._get_subspace_data_for_processing = get_subspace_data_for_processing
        self._execution_element_is_finished = execution_element_is_finished

        self.execution_element_failed: bool = False

    def finished_result_exists(self) -> bool:
        """
        (If the finished result already exists the ExecutionElements doesn't need to be computed again.
        -> Used for performance improvement.) \n
        :return: True if the finished result exists. Otherwise, return False.
        """
        return os.path.isfile(self._result_path)

    # Schedulable
    @property
    def user_id(self) -> int:
        """
        :return:  The ID of the user belonging to this Execution.
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
        Is called by the Scheduler. \n
        Will compute and store the result of the ExecutionElement. \n
        :return: None
        """

        try:
            run_algo_result: np.ndarray = self.__run_algorithm()
            result_to_save: np.ndarray = self.__convert_result_to_csv(run_algo_result)
            DataIO.write_csv(self._result_path, result_to_save)
        except Exception as e:
            self.execution_element_failed = True

        # ExecutionElement finished
        self._execution_element_is_finished(self.execution_element_failed)

    # do_work()
    def __run_algorithm(self) -> np.ndarray:
        """
        Computes the algorithms on the subspace. \n
        :return: Returns the result of the algorithm on the subspace.
        """
        ss_shm = self._get_subspace_data_for_processing()
        ss_dim_count = self._subspace.get_included_dimension_count()
        ss_point_count = ss_shm.size / self._subspace_dtype.itemsize / ss_dim_count
        ss_arr = np.ndarray((ss_point_count, ss_dim_count), dtype=self._subspace_dtype,
                            buffer=ss_shm)
        algo = AlgorithmLoader.get_algorithm_object(self._algorithm.path, self._algorithm.hyper_parameter)
        results = algo.decision_function(ss_arr)
        ss_shm.close()
        return results

    def __convert_result_to_csv(self, run_algo_result: np.ndarray) -> np.ndarray:
        """
        Converts the algorithm result into the csv-file that will be stored. \n
        :param run_algo_result: The unchanged result of the algorithm.
        :return: The result-csv-file of this ExecutionElement.
        """
        one_to_n = np.arange(0, run_algo_result.shape[0], 1, self._subspace_dtype)
        return np.concatenate((one_to_n.T, run_algo_result), 1)
