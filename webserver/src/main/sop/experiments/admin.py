from django.contrib import admin

from experiments.forms.admin import AdminAlgorithm
from experiments.models.algorithm import Algorithm
from experiments.models.dataset import Dataset
from experiments.models.execution import Execution
from experiments.models.experiment import Experiment

admin.site.register(Dataset)
admin.site.register(Experiment)
admin.site.register(Execution)


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    form = AdminAlgorithm
    list_display = ["name", "group", "description", "user"]
    readonly_fields = ["upload_date"]
    raw_id_fields = ["user"]
    list_filter = ["name"]
    search_fields = ["group", "name"]

    # override to get current user in form
    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user
        return form
