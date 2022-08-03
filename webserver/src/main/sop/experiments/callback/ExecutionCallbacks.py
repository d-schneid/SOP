import os

from backend.task import TaskState
from backend.task.execution.core.Execution import Execution as BackendExecution
from experiments.models import Execution
from experiments.models.execution import get_zip_result_path


def execution_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:
    """
    The progress callback function used by the backend execution task. It will update
    the progress and state of an execution model based on the progress and state of the
    backend task.
    @param task_id: the task id of the backend task which will be the executions primary
    key
    @param task_state: The TaskState of the backend execution.
    @param progress: The progress of the backend execution.
    @return: None
    """
    print("execution callback", task_id, task_state, progress)
    execution: Execution = Execution.objects.get(pk=task_id)

    if task_state.is_finished():
        zip_path = get_zip_result_path(execution)
        assert os.path.exists(zip_path)
        execution.result_path.name = get_zip_result_path(execution)

    execution.status = task_state.name
    execution.progress = progress

    execution.save()


def metric_callback(execution: BackendExecution) -> None:
    """
    The metric callback used by the backend execution task. It calls metrics in the
    backend and saves their results in the executions results path before it is zipped.
    @param execution: The backend execution object on which the metrics will be called.
    @return: None
    """
    print("METRIC CALLBACK!!")
