from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from authentication.models import User


class AlgorithmManager(models.Manager):
    pass


class AlgorithmQuerySet(models.QuerySet):

    # TODO: type hints
    def get_sorted_by_group_and_name(self):
        return self.order_by("group", Lower("name"))

    def get_sorted_by_name(self):
        return self.order_by(Lower("name"))

    def get_with_group(self, group):
        return self.filter(group=group)

    def get_by_user_and_public(self, user):
        return self.filter(Q(user_id__exact=user.id) | Q(user_id__exact=None))

    def get_sorted_by_upload_date(self):
        # latest uploaded algorithms first
        return self.order_by("-upload_date")


class DatasetManager(models.Manager):
    pass


class DatasetQueryset(models.QuerySet):
    def get_sorted_by_name(self):
        return self.order_by(Lower("name"))

    def get_sorted_by_upload_time(self):
        return self.order_by("-upload_date")

    def get_by_user(self, request_user: User):
        return self.filter(user=request_user)


class ExperimentManager(models.Manager):
    pass


class ExperimentQueryset(models.QuerySet):
    def get_sorted_by_name(self):
        return self.order_by(Lower("display_name"))

    def get_sorted_by_creation_date(self):
        return self.order_by("-creation_date")

    def get_by_user(self, request_user: User):
        return self.filter(user=request_user)

    def get_with_dataset(self, request_dataset):
        return self.filter(dataset=request_dataset)


class ExecutionManager(models.Manager):
    pass


class ExecutionQueryset(models.QuerySet):
    def get_sorted_by_creation_date(self):
        return self.order_by("-creation_date")

    def get_by_user(self, request_user: User):
        return self.filter(user=request_user)
