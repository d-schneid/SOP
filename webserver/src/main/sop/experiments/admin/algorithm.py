from typing import Optional

from django.contrib import admin, messages
from django.contrib.admin.actions import delete_selected as django_delete_selected
from django.db.models import Model
from django.http import HttpRequest, HttpResponse

from experiments.forms.admin import AdminAddAlgorithmForm, AdminChangeAlgorithmForm
from experiments.models.algorithm import Algorithm
from experiments.models.experiment import Experiment
from experiments.models.managers import AlgorithmQuerySet


class ExperimentInline(admin.StackedInline[Model, Experiment]):
    model = Experiment.algorithms.through
    verbose_name = "Experiment"
    template = "experiment_inline.html"

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin[Algorithm]):
    inlines = [ExperimentInline]
    list_display = ["display_name", "group", "user", "upload_date"]
    raw_id_fields = ["user"]
    list_filter = ["user", "group"]
    search_fields = ["name"]
    actions = ["delete_selected"]

    # override to get current user in form
    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user  # type: ignore
        return form

    def add_view(self, request, form_url="", extra_context=None):
        self.form = AdminAddAlgorithmForm
        return super().add_view(request, form_url, extra_context)

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url="",
        extra_context: Optional[dict[str, object]] = None,
    ):
        self.form = AdminChangeAlgorithmForm
        return super().change_view(request, object_id, form_url, extra_context)

    # adjust behavior of deletion of model
    def delete_view(
        self,
        request: HttpRequest,
        object_id: str,
        extra_context: Optional[dict[str, object]] = None,
    ) -> HttpResponse:
        algorithm: Algorithm | None = self.get_object(request, object_id)
        assert algorithm is not None  # TODO: handle algorithm is None

        if algorithm.experiment_set.count() > 0:  # type: ignore
            messages.error(
                request,
                "This algorithm cannot be deleted, "
                "since it is used in at least one experiment (see below)",
            )
            return self.change_view(request, object_id, "", extra_context)
        return super().delete_view(request, object_id, extra_context)

    # adjust behavior of deletion of queryset
    def delete_selected(self, request: HttpRequest, obj: AlgorithmQuerySet):
        algorithms = obj.all()
        for algorithm in algorithms:
            if algorithm.experiment_set.count() > 0:  # type: ignore
                messages.error(
                    request,
                    "Bulk deletion cannot be executed, "
                    f"since at least algorithm {algorithm.display_name} is used in at least one experiment",
                )
                return
        return django_delete_selected(self, request, algorithms)

    # remove inlines from add_view
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []
