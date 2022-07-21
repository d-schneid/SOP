from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet
from django.contrib.admin.actions import delete_selected as django_delete_selected

from typing import Optional, Dict, Any

from experiments.models import Dataset, Experiment
from experiments.models.managers import DatasetQuerySet


@admin.register(Dataset)  # TODO: nochmal alles durchgehen und kontrollieren (-Finn)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ["display_name", "user", "datapoints_total", "dimensions_total", "upload_date", "is_cleaned"]
    list_filter = ["user", "upload_date", "is_cleaned"]
    search_fields = ["display_name"]
    actions = ["delete_selected"]

    def delete_view(
        self, request: HttpRequest, object_id: str, extra_context: Optional[Dict[str, Any]] = ...
    ) -> HttpResponse:

        dataset: Optional[Dataset] = self.get_object(request, object_id)

        if dataset is None:
            return HttpResponse("Error.")  # TODO: besserer machen, redirect oder so

        # check, if dataset is used in an experiment
        experiments_dependent: QuerySet = Experiment.objects.filter(dataset__pk=dataset.pk)
        if len(experiments_dependent) > 0:
            messages.error(
                request,
                "This dataset cannot be deleted, as it is used in at least one experiment."
                " (See below for further detail)",
            )
            return self.change_view(request, object_id, "", extra_context)
        return super().delete_view(request, object_id, extra_context)

    def delete_selected(self, request: HttpRequest, obj: DatasetQuerySet):
        # check, if at least one dataset is used in one experiment
        for dataset in obj.all():
            experiments_dependent: QuerySet = Experiment.objects.filter(dataset__pk=dataset.pk)

            if len(experiments_dependent) > 0:
                messages.error(
                    request,
                    "These datasets cannot be deleted, as at least the dataset '{name}' is"
                    " used in an experiment".format(name=dataset.display_name),
                )
                return
            return django_delete_selected(self, request, obj.all())


