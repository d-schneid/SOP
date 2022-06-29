import string
from collections.abc import Iterable
from typing import List

from backend_library.src.main.backend.task.execution.core.Execution import Execution
from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace
from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.task.execution.core.ExecutionElement import ExecutionElement
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler

class ExecutionSubspace:
    def __init__(self, execution: Execution, subspace: Subspace):
        self._execution: Execution = execution
        self._subspace: Subspace = subspace

        algorithms: Iterable[ParameterizedAlgorithm] = execution.algorithms

        # further private variables
        self._finished_execution_element_count: int = 0
        self._total_execution_element_count: int = TaskHelper.iterable_length(algorithms)
        self._execution_elements: List[ExecutionElement] = list()

        # shared memory
        self._subspace_shared_memory_name: string = ""

        # initialisation functions
        self.__generate_execution_elements(algorithms)
        self.__schedule_execution_elements()

    def __generate_execution_elements(self, algorithms: Iterable[ParameterizedAlgorithm]) -> None:
        for algorithm in algorithms:
            self._execution_elements.append(ExecutionElement(self, algorithm))

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
