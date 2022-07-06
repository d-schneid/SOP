from django.urls import path
from django.views.generic import RedirectView

from experiments.views.dataset import DatasetOverview, DatasetDetailView
from .views.algorithm import (
    AlgorithmEditView,
    AlgorithmUploadView,
    AlgorithmDeleteView,
    AlgorithmOverview,
)

urlpatterns = [
    path(
        "algorithm/",
        RedirectView.as_view(pattern_name="algorithm_overview",
                             permanent=True),
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
        "algorithm/<int:pk>/edit/", AlgorithmEditView.as_view(),
        name="algorithm_edit"
    ),
    path("algorithm/upload/", AlgorithmUploadView.as_view(),
         name="algorithm_upload"),
    # Dataset URLs
    path("dataset/overview/", DatasetOverview.as_view(),
         name="dataset_overview"),
    path("dataset/<int:pk>/", DatasetDetailView.as_view(),
         name="dataset_detail_view"),
]
