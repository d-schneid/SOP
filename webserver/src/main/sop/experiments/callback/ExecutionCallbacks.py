import os

from backend.task import TaskState
from backend.task.execution.core.Execution import Execution as BackendExecution
from experiments.models import Execution
from experiments.models.execution import get_zip_result_path, ExecutionStatus


def execution_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:
    print("execution callback", task_id, task_state, progress)
    execution: Execution = Execution.objects.get(pk=task_id)

    if task_state.is_finished():
        zip_path = get_zip_result_path(execution)
        assert os.path.exists(zip_path)
        execution.result_path.name = get_zip_result_path(execution)

    if task_state.is_finished() and not task_state.error_occurred():
        execution.status = ExecutionStatus.FINISHED.name
    elif task_state.is_finished() and task_state.error_occurred():
        execution.status = ExecutionStatus.FINISHED_WITH_ERROR.name
    elif task_state.is_running() and not task_state.error_occurred():
        execution.status = ExecutionStatus.RUNNING.name
    elif task_state.is_running() and task_state.error_occurred():
        execution.status = ExecutionStatus.RUNNING_WITH_ERROR.name

    execution.progress = progress

    execution.save()


def metric_callback(execution: BackendExecution) -> None:
    print("METRIC CALLBACK!!")
