import os

from backend.DatasetInfo import DatasetInfo
from backend.task import TaskState
from experiments.models import Dataset


def cleaning_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:

    dataset: Dataset = Dataset.objects.get(pk=task_id)

    # if the task has finished, update the database
    if task_state.is_finished() and not task_state.error_occurred():

        dataset.datapoints_total = DatasetInfo.get_dataset_datapoint_amount(dataset.path_cleaned.path)
        dataset.dimensions_total = DatasetInfo.get_dataset_dimension(dataset.path_cleaned.path)
        dataset.is_cleaned = True

        # also, check for assertions
        assert os.path.exists(dataset.path_cleaned.path)

    elif task_state.is_finished() and task_state.error_occurred():
        pass  # TODO: braucht extra model parameter

    dataset.save()
