import os
import shutil
from pathlib import Path
from typing import Any

from django.db.models.signals import post_delete
from django.dispatch import receiver

from backend.scheduler.Scheduler import Scheduler
from experiments.models import Algorithm, Dataset, Execution
from experiments.models.execution import get_result_path


def _delete_file(path_name: str) -> None:
    path = Path(path_name)
    if os.path.isfile(path):
        os.unlink(path)
    if os.path.isdir(path.parent):
        if not any(os.scandir(path.parent)):
            # Directory for user will be created again once user uploads a file
            os.rmdir(path.parent)


# Signal handlers delete all the respective files of a user
# when user gets deleted by catching the signals from CASCADE.
# If respective model instance on its own gets deleted,
# signal handlers will trigger as well.
# Signal handlers trigger on any delete operation of the respective model instance.


@receiver(post_delete, sender=Algorithm)
def delete_algorithm_file(
        sender: Algorithm, instance: Algorithm, *args: Any, **kwargs: Any
) -> None:
    if instance.path:
        _delete_file(instance.path.path)


@receiver(post_delete, sender=Dataset)
def delete_dataset_file(
        sender: Dataset, instance: Dataset, *args: Any, **kwargs: Any
) -> None:
    if instance.path_original:
        _delete_file(instance.path_original.path)
    if instance.path_cleaned:
        _delete_file(instance.path_cleaned.path)


@receiver(post_delete, sender=Execution)
def delete_result_file(
        sender: Execution, instance: Execution, *args: Any, **kwargs: Any
) -> None:
    if instance.is_running and instance.pk is not None:
        Scheduler.get_instance().abort_by_task(task_id=instance.pk)
        working_directory = get_result_path(instance)
        if os.path.isdir(working_directory):
            shutil.rmtree(working_directory)

    if instance.result_path:
        _delete_file(instance.result_path.path)
