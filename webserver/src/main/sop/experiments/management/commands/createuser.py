from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandParser

from authentication.models import User


class Command(BaseCommand):
    help = "Creates a new user with the given parameters"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--username",
            required=True,
            type=str,
            help="The username of the user"
        )
        parser.add_argument(
            "--password",
            required=True,
            type=str,
            help="The password of the user"
        )
        parser.add_argument(
            "--staff",
            action="store_true",
            help="Give the user the staff rank"
        )
        parser.add_argument(
            "--admin",
            action="store_true",
            help="Give the user the admin rank"
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:

        # check, if a user with same username already exists
        if User.objects.filter(username=options["username"]).exists():
            self.stdout.write(self.style.ERROR("A user with this username already exists;"
                                               " the username has to be unique."))
            return None

        # create a user with the specified properties
        user = User.objects.create_user(
            username=options["username"],
            password=options["password"]
        )
        user.is_staff = options["staff"]
        user.is_superuser = options["admin"]
        user.save()

        # output the created user object
        output = ("The following user object was created:  " +
                  "Username: " + options["username"] + " | " +
                  "Password: " + options["password"] + " | " +
                  "Is Staff: " + str(options["staff"]) + " | " +
                  "Is Admin: " + str(options["admin"])
                  )
        self.stdout.write(self.style.SUCCESS(output))
        return None
