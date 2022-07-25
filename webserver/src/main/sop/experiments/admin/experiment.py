from typing import Sequence, Optional

from django.contrib import admin
from django.http import HttpRequest

from experiments.models.experiment import Experiment


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin[Experiment]):
    list_display = ["display_name", "user", "creation_date"]
    raw_id_fields = ["user"]
    list_filter = ["creation_date"]
    search_fields = ["display_name",
                     "user__username",
                     "algorithms__display_name",
                     "dataset__display_name"]

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Experiment] = None) -> Sequence[str]:
        # for editing an existing experiment
        if obj:
            return ["user", "dataset", "algorithms"]
        # for adding a new experiment
        else:
            return []