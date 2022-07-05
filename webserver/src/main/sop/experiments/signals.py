import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from experiments.models import Algorithm


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)
    if not any(os.scandir(os.path.dirname(path))):
        # Directory for user will be created again once user uploads a file
        os.rmdir(os.path.dirname(path))


# Delete all algorithm files (.py) of a user when user gets deleted by catching the signals from CASCADE
# If algorithm on its own gets deleted, this will trigger as well
# Triggers on any delete operations of an algorithm
# TODO: does not work, signal is not even received wtf?!
@receiver(post_delete, sender=Algorithm)
def delete_algorithm_file(sender, instance, *args, **kwargs):
    print("Signal received!")
    if instance.path:
        _delete_file(instance.path.path)
