import os
import string
from abc import ABC

import ExecutionSubspace as es
import numpy as np

from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend_library.src.main.backend.scheduler.Schedulable import Schedulable
from backend_library.src.main.backend.DataIO import DataIO


class ExecutionElement(Schedulable, ABC):
    """
    Is the smallest unit of an Execution.
    Consists of the computation of one algorithm on exactly one subspace.
    """
    def __init__(self, execution_subspace: es.ExecutionSubspace, algorithm: ParameterizedAlgorithm,
                 result_path: string):
        """
        :param execution_subspace: The ExecutionSubspace that belongs to this ExecutionElement.
        :param algorithm: The algorithm that should be computed on the subspace.
        :param result_path: The directory where the result-csv-file of the ExecutionElement-computation will be stored.
        """
        self._execution_subspace: es.ExecutionSubspace = execution_subspace
        self._algorithm: ParameterizedAlgorithm = algorithm
        self._result_path: string = result_path

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
        # TODO: Tobias
        return np.zeros(0)

    def __convert_result_to_csv(self, run_algo_result: np.ndarray) -> np.ndarray:
        """
        Converts the algorithm result into the csv-file that will be stored. \n
        :param run_algo_result: The unchanged result of the algorithm.
        :return: The result-csv-file of this ExecutionElement.
        """
        # TODO: Tobias
        return np.zeros(0)
