from django.contrib import admin

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