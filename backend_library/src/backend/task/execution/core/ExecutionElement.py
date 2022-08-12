from __future__ import annotations

import os
from multiprocessing.shared_memory import SharedMemory
from typing import Callable, Optional

import numpy as np

from backend.DataIO import DataIO
from backend.scheduler.Schedulable import Schedulable
from backend.task.TaskHelper import TaskHelper
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.subspace.Subspace import Subspace


class ExecutionElement(Schedulable):
    """
    Is the smallest unit of an Execution.
    Consists of the computation of one algorithm on exactly one subspace.
    """

    def __init__(self, user_id: int, task_id: int, subspace: Subspace,
                 algorithm: ParameterizedAlgorithm, result_path: str,
                 subspace_dtype: np.dtype, ss_shm_name: str,
                 execution_element_is_finished: Callable[[bool, bool], None],
                 datapoint_count: int, row_numbers: np.ndarray, priority: int = 10):
        """
        :param user_id: The ID of the user belonging to this ExecutionElement. Has to be at least -1.
        :param task_id: The ID of this task. Has to be at least -1.
        :param subspace: The subspace on which the algorithm should compute its result.
        :param algorithm: The algorithm that should be computed on the subspace.
        :param result_path: The directory where the result-csv-file of the ExecutionElement-computation will be stored.
        :param subspace_dtype: The dtype of the values that are stored in the dataset for processing.
        :param ss_shm_name: The name of the shared memory containing the subspace data
        :param execution_element_is_finished: Reports the ExecutionSubspace that it finished its execution.
        :param row_numbers: the row numbers of the dataset, see AnnotatedDataset.row_mapping
        """
        assert priority <= 100
        assert priority >= 10

        assert user_id >= -1
        assert task_id >= -1

        self._user_id: int = user_id
        self._task_id: int = task_id
        self._priority: int = priority

        self._row_numbers = row_numbers
        self._datapoint_count = datapoint_count
        self._subspace: Subspace = subspace
        self._algorithm: ParameterizedAlgorithm = algorithm

        self._result_path: str = result_path
        self._subspace_dtype: np.dtype = subspace_dtype

        self._ss_shm_name: str = ss_shm_name
        self._execution_element_is_finished = execution_element_is_finished

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

    def do_work(self) -> int:
        """
        Is called by the Scheduler. \n
        Will compute and store the result of the ExecutionElement. \n
        :return: An exitcode provided to run_later_on_main
        """

        try:
            run_algo_result: np.ndarray = self.__run_algorithm()
            result_to_save: np.ndarray = self.__convert_result_to_csv(run_algo_result)
            DataIO.write_csv(self._result_path, result_to_save, add_index_column=False)
        except Exception as e:
            error_message = str(e)
            if error_message == "":
                error_message = "Error occurred while processing the ExecutionElement"
            TaskHelper.save_error_csv(self._result_path, error_message)
            return -1

        # ExecutionElement finished
        return 0

    # do_work()
    def __run_algorithm(self) -> np.ndarray:
        """
        Computes the algorithms on the subspace. \n
        :return: Returns the result of the algorithm on the subspace.
        """
        ss_shm = SharedMemory(self._ss_shm_name)
        ss_dim_count = self._subspace.get_included_dimension_count()
        ss_arr = np.ndarray((self._datapoint_count, ss_dim_count),
                            dtype=self._subspace_dtype, buffer=ss_shm.buf)
        algo = AlgorithmLoader.get_algorithm_object(self._algorithm.path,
                                                    self._algorithm.hyper_parameter)
        algo.fit(ss_arr, None)
        results = algo.decision_function(ss_arr)
        ss_shm.close()
        return results

    def __convert_result_to_csv(self, run_algo_result: np.ndarray) -> np.ndarray:
        """
        Converts the algorithm result into the csv-file that will be stored. \n
        :param run_algo_result: The unchanged result of the algorithm.
        :return: The result-csv-file of this ExecutionElement.
        """
        rows = np.expand_dims(self._row_numbers.astype(object), 1)

        data = np.expand_dims(run_algo_result.astype(object), 1)
        rows_data = np.concatenate((rows, data), 1)
        return rows_data

    def run_later_on_main(self, statuscode: Optional[int]) -> None:
        self._execution_element_is_finished(statuscode != 0, statuscode is None)
