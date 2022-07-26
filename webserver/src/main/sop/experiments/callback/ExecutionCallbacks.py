from backend.task import TaskState

from experiments.models import Execution


def execution_callback(task_id: int, task_state: TaskState.TaskState, progress: float) -> None:
    execution: Execution = Execution.objects.get(pk=task_id)

    execution.status = task_state.name
    execution.progress = progress

    execution.save()


def metric_callback(execution: Execution) -> None:
    print("METRIC CALLBACK!!")
    print(
        execution.pk,
        execution.result_path,
        "created at",
        execution.creation_date,
        "finished at",
        execution.finished_date,
    )
