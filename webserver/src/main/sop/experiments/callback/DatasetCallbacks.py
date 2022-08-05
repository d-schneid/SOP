import os

from backend.DatasetInfo import DatasetInfo
from backend.task import TaskState
from experiments.models.dataset import Dataset, CleaningState


def cleaning_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:

    dataset: Dataset = Dataset.objects.get(pk=task_id)

    # if the task has finished, update the database
    if task_state.is_finished():
        if task_state.error_occurred():
            dataset.status = CleaningState.FINISHED_WITH_ERROR.name

            # assert that the error message is available
            # TODO

        else:
            dataset.status = CleaningState.FINISHED.name

            dataset.datapoints_total = DatasetInfo.get_dataset_datapoint_amount(dataset.path_cleaned.path)
            dataset.dimensions_total = DatasetInfo.get_dataset_dimension(dataset.path_cleaned.path)

            # check for the cleaned file to exist
            assert os.path.exists(dataset.path_cleaned.path)

    dataset.save()
