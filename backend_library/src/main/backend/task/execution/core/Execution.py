import os
import string
from typing import Callable

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend_library.src.main.backend.task.execution.core.ExecutionSubspace import ExecutionSubspace
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler


class Execution(Task):

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable, dataset_path: string,
                 result_path: string, subspace_generation: SubspaceGenerationDescription, algorithms,
                 metric_callback: Callable):
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

    def generate_file_system_structure(self):
        pass

    def result_root_folder_exists(self) -> bool:
        return False

    def generate_execution_details_in_filesystem(self):
        return False

    def generate_execution_subspaces(self):
        for subspace in self.subspaces:
            ExecutionSubspace(self, subspace)

    # schedule
    def schedule(self) -> None:
        if self.does_zip_exists():
            self.task_progress_callback(self.task_id, TaskState.FINISHED, 1.0)
            return
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(Execution)

    def does_zip_exists(self) -> bool:
        return os.path.isfile(self.get_zip_path())

    def get_zip_path(self) -> string:
        # Todo. Thing if is enough:
        return self.result_path + ".zip"

