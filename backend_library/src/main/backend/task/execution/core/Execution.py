import string
from typing import Callable

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.execution.subspace.SubspaceGenerationDescription import SubspaceGenerationDescription


class Execution(Task):

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable, dataset_path: string, result_path: string, subspace_generation: SubspaceGenerationDescription, algorithms, metric_callback: Callable):
        Task.__init__(self, user_id, task_id, task_progress_callback)
        self.dataset_path: string = dataset_path
        self.result_path: string = result_path
        self.subspace_generation: SubspaceGenerationDescription = subspace_generation
        self.algorithms = algorithms
        self.metric_callback: Callable = metric_callback

        # further private variables
        self.has_failed_element: bool = False
        self.finished_execution_element_count: int = 0
        # TODO generate subspaces
        self.subspaces = None
        self.total_execution_element_count: int = self.subspaces.len() * algorithms.len()
        # TODO generate shared memory
        self.shared_memory_name: string = ""
