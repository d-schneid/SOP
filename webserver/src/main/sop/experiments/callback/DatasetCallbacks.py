from backend.task import TaskState
from experiments.models import Dataset


def cleaning_callback(task_id: int, task_state: TaskState.TaskState, progress: float) -> None:
    dataset: Dataset = Dataset.objects.get(uuid=task_id)

    # if the task has finished, update the database
    if task_state == TaskState.TaskState.FINISHED:
        dataset.is_cleaned = True
    elif task_state == TaskState.TaskState.FINISHED_WITH_ERROR:
        pass  # TODO: braucht extra model parameter

    dataset.save()
