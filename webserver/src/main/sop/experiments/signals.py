import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from experiments.models import Algorithm, Dataset, Execution


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)
    if not any(os.scandir(os.path.dirname(path))):
        # Directory for user will be created again once user uploads a file
        os.rmdir(os.path.dirname(path))


# Signal handlers delete all the respective files of a user
# when user gets deleted by catching the signals from CASCADE.
# If respective model instance on its own gets deleted,
# signal handlers will trigger as well.
# Signal handlers trigger on any delete operation of the respective model instance.

@receiver(post_delete, sender=Algorithm)
def delete_algorithm_file(sender, instance, *args, **kwargs):
    if instance.path:
        _delete_file(instance.path.path)


@receiver(post_delete, sender=Dataset)
def delete_dataset_file(sender, instance, *args, **kwargs):
    if instance.path_original:
        _delete_file(instance.path_original.path)
    if instance.path_cleaned:
        _delete_file(instance.path_cleaned.path)


@receiver(post_delete, sender=Execution)
def delete_result_file(sender, instance, *args, **kwargs):
    if instance.result_path:
        _delete_file(instance.result_path.path)