from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom database model of a User.
    """

    @property
    def id(self) -> int:
        return hash(self.username)
