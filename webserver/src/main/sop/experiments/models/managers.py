from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from authentication.models import User


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

    def get_sorted_by_upload_date(self):
        # latest uploaded algorithms first
        return self.order_by('-upload_date')


class AlgorithmManager(models.Manager):
    pass


class ExecutionManager(models.Manager):
    pass


class DatasetManager(models.Manager):
    pass


class DatasetQueryset(models.QuerySet):
    def get_sorted_by_name(self):
        return self.order_by(Lower('name'))

    def get_sorted_by_upload_time(self):
        # TODO: implement
        return self.order_by("name")

    def get_by_user(self, request_user: User):
        return self.filter(user=request_user)
