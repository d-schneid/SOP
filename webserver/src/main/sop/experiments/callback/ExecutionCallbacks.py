from backend.task import TaskState
from backend.task.execution.core.Execution import Execution as BackendExecution
from experiments.models import Execution
from experiments.models.execution import get_result_path


def execution_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:
    print("execution callback", task_id, task_state, progress)
    execution: Execution = Execution.objects.get(pk=task_id)

    if task_state.is_finished():
        execution.result_path.name = get_result_path(execution)

    execution.status = task_state.name
    execution.progress = progress

    execution.save()


def metric_callback(execution: BackendExecution) -> None:
    print("METRIC CALLBACK!!")
