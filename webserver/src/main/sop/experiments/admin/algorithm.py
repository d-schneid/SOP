from __future__ import annotations

from typing import Type, Optional, Sequence, List

from django.contrib import admin
from django.http import HttpRequest
from django.urls import re_path, reverse
from django.urls.resolvers import URLPattern
from django.utils.html import format_html

from experiments.admin.inlines import ExperimentInlineAlgorithm
from experiments.admin.abstract_model_admin import AbstractModelAdmin
from experiments.forms.admin.algorithm import AdminAddAlgorithmForm
from experiments.models.algorithm import Algorithm
from experiments.views.algorithm import download_algorithm


@admin.register(Algorithm)
class AlgorithmAdmin(AbstractModelAdmin):
    inlines = [ExperimentInlineAlgorithm]
    list_display = ["display_name", "group", "user", "upload_date"]
    raw_id_fields = ["user"]
    list_filter = ["upload_date", "group"]
    search_fields = ["display_name", "user__username", "group", "description"]
    actions = ["delete_selected"]

    def get_admin_add_form(self) -> Type[AdminAddAlgorithmForm]:
        return AdminAddAlgorithmForm

    def get_model_name(self) -> str:
        return "algorithm"

    def get_readonly_fields(self,
                            request: HttpRequest,
                            obj: Optional[Algorithm] = None
    ) -> Sequence[str]:
        # for editing an existing experiment
        if not (obj is None):
            return ["signature", "user", "upload_date", "download"]
        # for adding a new experiment
        else:
            return []

    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        urls += [
            re_path(r'^algorithm_download/(?P<pk>\d+)$',
                    download_algorithm,
                    name='experiments_algorithm_download'),
        ]
        return urls

    def download(self, algorithm: Algorithm) -> str:
        return format_html(
            '<a href="{}">Download</a>',
            reverse('admin:experiments_algorithm_download', args=[algorithm.pk])
        )
    download.short_description = "Algorithm"
