from django.conf import settings
from django.db import models


class Dataset(models.Model):
    _name = models.CharField(max_length=80)
    _description = models.TextField()
    _user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    _datapoints_total = models.IntegerField()
    _dimensions_total = models.IntegerField()
    _path_original = models.FileField()
    _path_cleaned = models.FilePathField()
    _is_cleaned = models.BooleanField()
    # TODO
    objects = ...
