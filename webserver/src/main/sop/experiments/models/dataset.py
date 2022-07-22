from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from experiments.models.managers import DatasetManager, DatasetQuerySet


def _get_dataset_upload_path(instance, filename) -> str:
    user_id = instance.user.id
    return f"datasets/user_{user_id}/{filename}"  # TODO: check -Finn


class Dataset(models.Model):
    """
    Database Model of a Dataset.
    """

    display_name = models.CharField(max_length=80)  # type: ignore
    description = models.TextField(max_length=255, blank=True)  # type: ignore
    upload_date = models.DateTimeField(auto_now_add=True)  # type: ignore
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # type: ignore
    datapoints_total = models.IntegerField()  # type: ignore
    dimensions_total = models.IntegerField()  # type: ignore
    path_original = models.FileField(
        upload_to=_get_dataset_upload_path,
        validators=(FileExtensionValidator(allowed_extensions=["csv"]),),
    )
    path_cleaned = models.FileField(null=True)
    is_cleaned = models.BooleanField(default=False)  # type: ignore
    objects = DatasetManager.from_queryset(DatasetQuerySet)()

    class Meta:
        """
        Contains meta-information about Dataset Model
        """

    @property
    def is_deletable(self) -> bool:
        # Import this here to avoid circular import
        from experiments.models import Experiment

        return not Experiment.objects.get_with_dataset(self).exists()

    def __str__(self) -> str:
        return str(self.display_name) + " | " + str(self.user)


def get_dataset_path(instance: Dataset, filename: str) -> str:
    return f"datasets/user_{instance.user.pk}/{filename}"
