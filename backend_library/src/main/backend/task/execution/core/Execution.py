import json
import multiprocessing
import os
import string
from typing import Callable, Optional
from typing import List
from collections.abc import Iterable

from backend_library.src.main.backend.task.Task import Task
from backend_library.src.main.backend.task.TaskState import TaskState
from backend_library.src.main.backend.task.TaskHelper import TaskHelper
from backend_library.src.main.backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend_library.src.main.backend.task.execution.core.ExecutionSubspace import ExecutionSubspace
from backend_library.src.main.backend.scheduler.Scheduler import Scheduler
from backend_library.src.main.backend.task.execution.ResultZipper import ResultZipper
from backend_library.src.main.backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace


class Execution(Task):
    cache_dataset_lock = multiprocessing.Lock()
    execution_element_finished_lock = multiprocessing.Lock()

    def __init__(self, user_id: int, task_id: int, task_progress_callback: Callable, dataset_path: string,
                 result_path: string, subspace_generation: SubspaceGenerationDescription, algorithms,
                 metric_callback: Callable):
        Task.__init__(self, user_id, task_id, task_progress_callback)
        self._dataset_path: string = dataset_path
        self._result_path: string = result_path
        self._subspace_generation: SubspaceGenerationDescription = subspace_generation
        self._algorithms = algorithms
        self._metric_callback: Callable = metric_callback

        # on created logic
        self.__fill_algorithms_directory_name()
        self.__generate_file_system_structure()
        self._zipped_result_path: string = self._result_path + ".zip"
        # further private variables
        self._has_failed_element: bool = False
        self._finished_execution_element_count: int = 0
        self._metric_finished: bool = False
        # generate subspaces
        self._subspaces: Iterable[Subspace] = self._subspace_generation.generate()
        self._subspaces_count = TaskHelper.iterable_length(self._subspaces)
        self._total_execution_element_count: int = self._subspaces_count * algorithms.len()
        # generate execution_subspaces
        self._execution_subspaces: List[ExecutionSubspace] = list()
        self.__generate_execution_subspaces()
        # shared memory
        self._shared_memory_name: string = ""

    def __fill_algorithms_directory_name(self):
        algorithm_display_name_dict: dict = {}

        for algorithm in self._algorithms:
            algorithm: ParameterizedAlgorithm = algorithm  # Done to get the type hint
            display_name: string = algorithm.display_name

            if (algorithm_display_name_dict.get(display_name)) is None:
                algorithm.directory_name_in_execution = display_name
            else:
                algorithm.directory_name_in_execution = display_name + " (" \
                                                        + algorithm_display_name_dict[display_name] + ")"

            algorithm_display_name_dict[algorithm.directory_name_in_execution] += 1

    # Generates all missing folders of the file system structure of this execution
    def __generate_file_system_structure(self) -> None:
        # if os.path.exists(self.result_path):
        if os.path.isdir(self._result_path):
            TaskHelper.create_directory(self._result_path)
            for algorithm in self._algorithms:
                algorithm_directory_path: string = self._result_path + '\\' + algorithm.display_name
                TaskHelper.create_directory(algorithm_directory_path)

    def __generate_execution_details_in_filesystem(self) -> None:
        details_path: string = self._result_path + 'details.json'

        # create dictionary that will be saved as a JSON-string
        details_dict = {'subspace_generation_information': self._subspace_generation.to_json()}
        for algorithm in self._algorithms:
            algorithm: ParameterizedAlgorithm = algorithm  # To get the type hint
            details_dict[algorithm.directory_name_in_execution] += algorithm.to_json()

        # save JSON-string
        details_json_string: string = json.dumps(details_dict)  # maybe set indent=4
        with open(details_path, 'w') as f:  # TODO: Test if this is correct
            json.dump(details_json_string, f)

    def __generate_execution_subspaces(self) -> None:
        for subspace in self._subspaces:
            self._execution_subspaces.append(ExecutionSubspace(self, subspace))

    # schedule
    def schedule(self) -> None:
        if self.__does_zip_exists():
            self._task_progress_callback(self._task_id, TaskState.FINISHED, 1.0)
            return
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(Execution)

    def __does_zip_exists(self) -> bool:
        return os.path.exists(self._zipped_result_path)

    def __compute_progress(self) -> float:
        execution_element_progress: float = self._finished_execution_element_count / self._total_execution_element_count;
        progress: float = max(execution_element_progress, 0.98)  # clamp the progress to be more accurate
        if self._metric_finished:
            progress += 0.01
        # Note: The 100% progress is only reached after zipping
        return progress

    # getter for ExecutionSubspace
    def get_user_id(self) -> int:
        return self._user_id

    def get_task_id(self) -> int:
        return self._task_id

    def cache_dataset(self) -> string:
        Execution.cache_dataset_lock.acquire()
        # TODO: Tobias
        Execution.cache_dataset_lock.release()
        pass

    def on_execution_element_finished(self, error: bool):
        if not self._has_failed_element and error:
            self._has_failed_element = True

        Execution.execution_element_finished_lock.acquire()
        self._finished_execution_element_count += 1
        if self._finished_execution_element_count == self._total_execution_element_count:
            self.__unload_dataset()
            self._metric_callback(self)
            self._metric_finished = True
            self.__schedule_result_zipping()
        Execution.execution_element_finished_lock.release()

    def __unload_dataset(self):
        # TODO: Tobias
        pass

    def __schedule_result_zipping(self):
        result_zipper: ResultZipper = ResultZipper(self._user_id, self._task_id, self._has_failed_element,
                                                   self._task_progress_callback, self._result_path,
                                                   self._zipped_result_path)
        scheduler: Scheduler = Scheduler.get_instance()
        scheduler.schedule(result_zipper)
