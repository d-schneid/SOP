from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom database model of a User.
    """

    @property
    def id(self) -> int:
        return hash(self.username)

