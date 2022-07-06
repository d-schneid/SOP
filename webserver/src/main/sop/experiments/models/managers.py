from django.db import models
from django.db.models.functions import Lower


class AlgorithmQuerySet(models.QuerySet):

    # TODO: type hints
    def get_sorted_by_group_and_name(self):
        return self.order_by('group', Lower('name'))

    def get_with_group(self, group):
        return self.filter(group = group)


class AlgorithmManager(models.Manager):
    pass


class ExecutionManager(models.Manager):
    pass


class DatasetManager(models.Manager):
    pass
