import os

from backend.DatasetInfo import DatasetInfo
from backend.task import TaskState
from experiments.models import Dataset


def cleaning_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:
    """
    The callback function used for backend callbacks. It will update values of the
    dataset based on the DatasetCleaning progress and state.
    @param task_id: The task_id of the cleaning which will be the datasets primary key.
    @param task_state: The TaskState of the DatasetCleaning.
    @param progress: The progress of the DatasetCleaning.
    @return: None
    """

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
