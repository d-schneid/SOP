import os

import pandas as pd

from backend.task import TaskState
from experiments.models import Dataset
from experiments.services.dataset import generate_path_dataset_cleaned


def cleaning_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:
    dataset: Dataset = Dataset.objects.get(pk=task_id)

    # if the task has finished, update the database
    if task_state.is_finished() and not task_state.error_occurred():
        cleaned_dataset_path = generate_path_dataset_cleaned(dataset.path_original.path)
        dataset.path_cleaned.name = cleaned_dataset_path
        assert os.path.exists(dataset.path_cleaned.path)
        csv_frame: pd.DataFrame = pd.read_csv(dataset.path_cleaned.path, header=None)
        dataset.datapoints_total = csv_frame.shape[0]  # number of lines
        dataset.dimensions_total = csv_frame.shape[1]  # number of columns
        dataset.is_cleaned = True
    elif task_state.is_finished() and task_state.error_occurred():
        pass  # TODO: braucht extra model parameter

    dataset.save()
