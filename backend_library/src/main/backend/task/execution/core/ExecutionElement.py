import os
import string
from abc import ABC

from ExecutionSubspace import ExecutionSubspace
import numpy as np

from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend_library.src.main.backend.scheduler.Schedulable import Schedulable


class ExecutionElement(Schedulable, ABC):
    def __init__(self, execution_subspace: ExecutionSubspace, algorithm: ParameterizedAlgorithm, result_path: string):
        self._execution_subspace: ExecutionSubspace = execution_subspace
        self._algorithm: ParameterizedAlgorithm = algorithm
        self._result_path: string = result_path

        self._user_id = self._execution_subspace.user_id
        self._task_id = self._execution_subspace.task_id

    def finished_result_exists(self) -> bool:
        return os.path.isfile(self._result_path)

    # Schedulable
    def user_id(self) -> int:
        return self._user_id

    def task_id(self) -> int:
        return self._task_id

    def do_work(self) -> None:
        run_algo_result: np.ndarray = self.__run_algorithm()
        result_to_save: np.ndarray = self.__convert_result_to_csv(run_algo_result)
        self.__save_result(self._result_path, result_to_save)

    # do_work()
    def __run_algorithm(self) -> np.ndarray:
        # TODO: Tobias
        return np.zeros(0)

    def __convert_result_to_csv(self, run_algo_result: np.ndarray) -> np.ndarray:
        # TODO: Tobias
        return np.zeros(0)

    def __save_result(self, path: string, result: np.ndarray) -> None:
        # TODO: Tobias
        pass
