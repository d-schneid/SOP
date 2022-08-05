from typing import Sequence, Optional, Dict

from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from experiments.models.experiment import Experiment
from experiments.forms.admin.experiment import AdminAddExperimentForm


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin[Experiment]):
    """
    The representation of the Experiment model in the admin interface.
    """
    list_display = ["display_name", "user", "creation_date"]
    raw_id_fields = ["user", "algorithms", "dataset"]
    list_filter = ["creation_date"]
    search_fields = ["display_name",
                     "user__username",
                     "algorithms__display_name",
                     "dataset__display_name"]

    def get_readonly_fields(self,
                            request: HttpRequest,
                            obj: Optional[Experiment] = None
    ) -> Sequence[str]:
        # for editing an existing experiment
        if not (obj is None):
            return ["user", "dataset", "algorithms", "creation_date"]
        # for adding a new experiment
        else:
            return []

    def add_view(self,
                 request: HttpRequest,
                 form_url: str = "",
                 extra_context: Optional[Dict[str, object]] = None
    ) -> HttpResponse:
        """
        View for the experiment model instance addition page in the admin interface.
        After adding a new experiment model instance, it redirects back to the change
        list.

        @param request: The HTTPRequest, this will be given by django.
        @param form_url: The URL of the form that shall be used for the add view.
        @param extra_context: Additional information that shall be presented by the
        add view.
        @return: A redirect to the change list.
        """
        self.form = AdminAddExperimentForm
        return super().add_view(request, form_url, extra_context)
