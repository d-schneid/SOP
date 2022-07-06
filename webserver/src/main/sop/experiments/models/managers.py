from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class AlgorithmQuerySet(models.QuerySet):

    # TODO: type hints
    def get_sorted_by_group_and_name(self):
        return self.order_by('group', Lower('name'))

    def get_sorted_by_name(self):
        return self.order_by(Lower('name'))

    def get_with_group(self, group):
        return self.filter(group=group)

    def get_by_user_and_public(self, user):
        return self.filter(
            Q(user_id__exact=user.id) | Q(user_id__exact=None)
        )

class AlgorithmManager(models.Manager):
    pass


class ExecutionManager(models.Manager):
    pass


class DatasetManager(models.Manager):
    def get_sorted_by_name(self):
        return super().get_queryset().order_by(Lower("name"))

    pass
