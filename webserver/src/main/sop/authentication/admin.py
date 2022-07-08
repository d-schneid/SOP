from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _

from .models import User

# Not needed, an admin (superuser) of the system shall have all possible permissions
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Custom User model that is displayed in the admin panel.
    """

    model = User

    list_filter = ("is_superuser", "is_active", "is_staff")
    list_display = ("username", "is_superuser", "is_active", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    # blocks a User
                    "is_active",
                    # User has all available permissions
                    "is_superuser",
                    # User can log in to admin site
                    "is_staff",
                ),
            },
        ),
    )
