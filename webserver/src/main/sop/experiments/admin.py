from django.contrib import admin, messages
from django.contrib.admin.actions import delete_selected as django_delete_selected

from experiments.forms.admin import AdminAddAlgorithmForm, AdminChangeAlgorithmForm
from experiments.models.algorithm import Algorithm
from experiments.models.dataset import Dataset
from experiments.models.execution import Execution
from experiments.models.experiment import Experiment


admin.site.register(Dataset)
admin.site.register(Experiment)
admin.site.register(Execution)


class ExperimentInline(admin.StackedInline):
    model = Experiment.algorithms.through
    verbose_name = "Experiment"
    verbose_name_plural = "Experiments"

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    inlines = [ExperimentInline]
    list_display = ["name", "group", "user", "upload_date"]
    raw_id_fields = ["user"]
    list_filter = ["user", "group"]
    search_fields = ["name"]
    actions = ["delete_selected"]

    # override to get current user in form
    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user
        return form

    def add_view(self, request, form_url="", extra_context=None):
        self.form = AdminAddAlgorithmForm
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.form = AdminChangeAlgorithmForm
        return super().change_view(request, object_id, form_url, extra_context)

    # adjust behavior of deletion of model
    def delete_view(self, request, object_id, extra_context=None):
        algorithm = self.get_object(request, object_id)
        if algorithm.experiment_set.count() > 0:
            messages.error(request, f"This algorithm cannot be deleted, "
                                    f"since it is used in at least one experiment (see below)")
            return self.change_view(request, object_id, "", extra_context)
        return super().delete_view(request, object_id, extra_context)

    # adjust behavior of deletion of queryset
    def delete_selected(self, request, obj):
        algorithms = obj.all()
        for algorithm in algorithms:
            if algorithm.experiment_set.count() > 0:
                messages.error(request, f"Bulk deletion cannot be executed, "
                                        f"since at least algorithm {algorithm.name} is used in at least one experiment")
                return
        return django_delete_selected(self, request, algorithms)