import json
import multiprocessing
import os
import string
from typing import Callable

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend_library.src.main.backend.task.execution.core.ExecutionSubspace import ExecutionSubspace
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler
from backend_library.src.main.backend.task.execution.ResultZipper import ResultZipper


class Execution(Task):

    cache_dataset_lock = multiprocessing.Lock()
    execution_element_finished_lock = multiprocessing.Lock()

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable, dataset_path: string,
                 result_path: string, subspace_generation: SubspaceGenerationDescription, algorithms,
                 metric_callback: Callable):
        Task.__init__(self, user_id, task_id, task_progress_callback)
        self.dataset_path: string = dataset_path
        self.result_path: string = result_path
        self.subspace_generation: SubspaceGenerationDescription = subspace_generation
        self.algorithms = algorithms
        self.metric_callback: Callable = metric_callback

        # on created logic
        self.generate_file_system_structure()
        self.zipped_result_path: string = self.result_path + ".zip"
        # further private variables
        self.has_failed_element: bool = False
        self.finished_execution_element_count: int = 0
        self.metric_finished: bool = False
        # TODO generate subspaces
        self.subspaces = None
        self.total_execution_element_count: int = self.subspaces.len() * algorithms.len()
        # TODO generate shared memory
        self.shared_memory_name: string = ""

    # Generates all missing folders of the file system structure of this execution
    def generate_file_system_structure(self) -> None:
        # if os.path.exists(self.result_path):
        TaskHelper.create_directory(self.result_path)
        for algorithm in self.algorithms:
            algorithm_directory_path: string = self.result_path + '\\' + algorithm.display_name
            TaskHelper.create_directory(algorithm_directory_path)
            # TODO: Denk nach was passiert, wenn 2 Algorithmen den selben Namen haben. Woher wissen die, in welchen
            #  Ordner die dann jeweils speichern müssen
        pass

    def result_root_folder_exists(self) -> bool:
        return os.path.exists(self.zipped_result_path)

    def generate_execution_details_in_filesystem(self) -> None:
        details_path: string = self.result_path + 'details.json'

        # create JSON-string that will be saved
        execution_details: string = self.subspace_generation.to_json() + "\n"
        for algorithm in self.algorithms:
            execution_details += algorithm.to_json() + "\n"

        # save JSON-string
        with open(details_path, 'w') as f:  # TODO: Test if this is correct
            json.dump(execution_details, f)

    def generate_execution_subspaces(self) -> None:
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

    def compute_progress(self) -> float:
        execution_element_progress: float = self.finished_execution_element_count / self.total_execution_element_count;
        progress: float = max(execution_element_progress, 0.98)  # clamp the progress to be more accurate
        if self.metric_finished:
            progress += 0.01
        # Note: The 100% progress is only reached after zipping
        return progress

    # getter for ExecutionSubspace
    def get_user_id(self) -> int:
        return self.user_id

    def get_task_id(self) -> int:
        return self.task_id

    def cache_dataset(self) -> string:
        Execution.cache_dataset_lock.acquire()
        # TODO: Tobias
        Execution.cache_dataset_lock.release()
        pass

    def on_execution_element_finished(self, error: bool):
        if not self.has_failed_element and error:
            self.has_failed_element = True

        Execution.execution_element_finished_lock.acquire()
        self.finished_execution_element_count += 1
        if self.finished_execution_element_count == self.total_execution_element_count:
            self.unload_dataset()
            self.metric_callback(self)
            self.metric_finished = True
            self.schedule_result_zipping()
        Execution.execution_element_finished_lock.release()

    def unload_dataset(self):
        # TODO: Tobias
        pass

    def schedule_result_zipping(self):
        result_zipper: ResultZipper = ResultZipper(self.user_id, self.task_id, self.has_failed_element,
                                                   self.task_progress_callback, self.result_path,
                                                   self.zipped_result_path)
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(result_zipper)
