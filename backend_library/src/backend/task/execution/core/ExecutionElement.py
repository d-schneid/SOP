from __future__ import annotations

import os

from abc import ABC

import numpy as np

from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.scheduler.Schedulable import Schedulable
from backend.DataIO import DataIO
from backend.task.execution.core import ExecutionSubspace


class ExecutionElement(Schedulable, ABC):
    """
    Is the smallest unit of an Execution.
    Consists of the computation of one algorithm on exactly one subspace.
    """

    def __init__(self, execution_subspace: ExecutionSubspace, algorithm: ParameterizedAlgorithm, result_path: str):
        """
        :param execution_subspace: The ExecutionSubspace that belongs to this ExecutionElement.
        :param algorithm: The algorithm that should be computed on the subspace.
        :param result_path: The directory where the result-csv-file of the ExecutionElement-computation will be stored.
        """
        self._execution_subspace: ExecutionSubspace = execution_subspace
        self._algorithm: ParameterizedAlgorithm = algorithm
        self._result_path: str = result_path

        self._user_id = self._execution_subspace.user_id
        self._task_id = self._execution_subspace.task_id

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
        return 0

    def do_work(self) -> None:
        """
        Is called by the Scheduler. \n
        Will compute and store the result of the ExecutionElement. \n
        :return: None
        """
        run_algo_result: np.ndarray = self.__run_algorithm()
        result_to_save: np.ndarray = self.__convert_result_to_csv(run_algo_result)
        DataIO.write_csv(self._result_path, result_to_save)

    # do_work()
    def __run_algorithm(self) -> np.ndarray:
        """
        Computes the algorithms on the subspace. \n
        :return: Returns the result of the algorithm on the subspace.
        """
        ss_shm = self._execution_subspace.get_subspace_data_for_processing
        ss_dim_count = self._execution_subspace.subspace.get_included_dimension_count()
        ss_point_count = ss_shm.size / self._execution_subspace.subspace_dtype.itemsize / ss_dim_count
        ss_arr = np.ndarray((ss_point_count, ss_dim_count), dtype=self._execution_subspace.subspace_dtype,
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
        one_to_n = np.arange(0, run_algo_result.shape[0], 1, self._execution_subspace.subspace_dtype)
        return np.concatenate((one_to_n.T, run_algo_result), 1)
