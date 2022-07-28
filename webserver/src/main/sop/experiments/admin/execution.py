from typing import Optional, Sequence

from django.contrib import admin
from django.http import HttpRequest

from experiments.models.execution import Execution


@admin.register(Execution)
class ExperimentAdmin(admin.ModelAdmin[Execution]):
    list_display = ["id", "experiment", "status", "creation_date"]
    list_filter = ["status", "creation_date"]
    search_fields = ["experiment__display_name"]

    def get_readonly_fields(self,
                            request: HttpRequest,
                            obj: Optional[Execution] = None
    ) -> Sequence[str]:
        # otherwise creation date will not be shown due to field type in execution model
        return ["creation_date"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self,
                              request: HttpRequest,
                              obj: Optional[Execution] = None
    ) -> bool:
        return False