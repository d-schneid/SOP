from typing import Optional, Sequence, List

from django.contrib import admin
from django.http import HttpRequest
from django.urls import re_path, reverse
from django.urls.resolvers import URLPattern
from django.utils.html import format_html
from django.utils.safestring import SafeString

from experiments.models.execution import Execution
from experiments.views.execution import download_execution_result_admin


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin[Execution]):
    """
    The representation of the Execution model in the admin interface.
    """
    list_display = ["id", "experiment", "status", "creation_date"]
    list_filter = ["status", "creation_date"]
    search_fields = ["experiment__display_name"]
    exclude = ["result_path"]

    def get_readonly_fields(self,
                            request: HttpRequest,
                            obj: Optional[Execution] = None
    ) -> Sequence[str]:
        if not obj is None:
            # creation date needs to be returned, otherwise it will not be shown
            # due to field type in execution model
            if obj.has_result:
                return ["creation_date", "download"]
            else:
                return ["creation_date"]
        return []

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self,
                              request: HttpRequest,
                              obj: Optional[Execution] = None
    ) -> bool:
        return False

    def get_urls(self) -> List[URLPattern]:
        """
        Adds custom view for downloading the result file of the associated
        Execution model instance to the URLs.
        :return: The URLs to be used for this ExecutionAdmin.
        """
        urls = super().get_urls()
        urls += [
            re_path(r'^execution_result_download/(?P<pk>\d+)$',
                    download_execution_result_admin,
                    name='experiments_execution_result_download'),
        ]
        return urls

    def download(self, execution: Execution) -> SafeString:
        """
        Custom field for this ExecutionAdmin.
        :return: Link to the custom function download_execution_result_admin.
        """
        return format_html(
            '<a href="{}">Download</a>',
            reverse('admin:experiments_execution_result_download', args=[execution.pk])
        )
    download.short_description = "Result"
