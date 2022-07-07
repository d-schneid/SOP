from django.urls import path
from django.views.generic import RedirectView

from experiments.views.algorithm import (
    AlgorithmEditView,
    AlgorithmUploadView,
    AlgorithmDeleteView,
    AlgorithmOverview,
)
from experiments.views.dataset import (
    DatasetOverview,
    DatasetUploadView,
    DatasetDeleteView,
    DatasetEditView
)

urlpatterns = [
    # Algorithm URLs
    path(
        "algorithm/",
        RedirectView.as_view(pattern_name="algorithm_overview", permanent=True),
    ),
    path(
        "algorithm/overview/",
        RedirectView.as_view(pattern_name="algorithm_overview_sorted",
                             permanent=True),
        {'sort': 'name'},
        name="algorithm_overview",
    ),
    path(
        "algorithm/overview/sort-by=<str:sort>/",
        AlgorithmOverview.as_view(),
        name="algorithm_overview_sorted",
    ),
    path(
        "algorithm/<int:pk>/delete/",
        AlgorithmDeleteView.as_view(),
        name="algorithm_delete",
    ),
    path(
        "algorithm/<int:pk>/edit/", AlgorithmEditView.as_view(), name="algorithm_edit"
    ),
    path("algorithm/upload/", AlgorithmUploadView.as_view(),
         name="algorithm_upload"),

    # Dataset URLs
    path("dataset/", RedirectView.as_view(pattern_name="dataset_overview", permanent=True)),
    path("dataset/overview/", DatasetOverview.as_view(), {"sort": "name"},
         name="dataset_overview"),
    path("dataset/overview/sort-by=<str:sort>/", DatasetOverview.as_view(), name="dataset_overview_sorted"),
    path("dataset/upload/", DatasetUploadView.as_view(),
         name="dataset_upload"),
    path("dataset/<int:pk>/delete/", DatasetDeleteView.as_view(), name="dataset_delete"),
    path("dataset/<int:pk>/edit/", DatasetEditView.as_view(), name="dataset_edit"),
]
