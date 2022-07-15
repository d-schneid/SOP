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
    DatasetEditView,
)
from experiments.views.execution import ExecutionCreateView, ExecutionDeleteView
from experiments.views.experiment import (
    ExperimentOverview,
    ExperimentCreateView,
    ExperimentDeleteView,
    ExperimentEditView,
)
from experiments.views.uploadhandler import upload_progress

urlpatterns = [
    # Algorithm URLs
    path(
        "algorithm/",
        RedirectView.as_view(pattern_name="algorithm_overview", permanent=True),
    ),
    path(
        "algorithm/overview/",
        RedirectView.as_view(pattern_name="algorithm_overview_sorted", permanent=True),
        {"sort": "name"},
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
    path("algorithm/upload/", AlgorithmUploadView.as_view(), name="algorithm_upload"),
    # Dataset URLs
    path(
        "dataset/",
        RedirectView.as_view(pattern_name="dataset_overview", permanent=True),
    ),
    path(
        "dataset/overview/",
        RedirectView.as_view(pattern_name="dataset_overview_sorted", permanent=True),
        {"sort": "name"},
        name="dataset_overview",
    ),
    path(
        "dataset/overview/sort-by=<str:sort>/",
        DatasetOverview.as_view(),
        name="dataset_overview_sorted",
    ),
    path("dataset/upload/", DatasetUploadView.as_view(), name="dataset_upload"),
    path(
        "dataset/<int:pk>/delete/", DatasetDeleteView.as_view(), name="dataset_delete"
    ),
    path("dataset/<int:pk>/edit/", DatasetEditView.as_view(), name="dataset_edit"),
    # Experiment URLs
    path(
        "experiment/",
        RedirectView.as_view(pattern_name="experiment_overview", permanent=True),
    ),
    path(
        "experiment/overview/",
        RedirectView.as_view(pattern_name="experiment_overview_sorted", permanent=True),
        {"sort": "name"},
        name="experiment_overview",
    ),
    path(
        "experiment/overview/sort-by=<str:sort>/",
        ExperimentOverview.as_view(),
        name="experiment_overview_sorted",
    ),
    path(
        "experiment/create/", ExperimentCreateView.as_view(), name="experiment_create"
    ),
    path(
        "experiment/<int:pk>/delete/",
        ExperimentDeleteView.as_view(),
        name="experiment_delete",
    ),
    path(
        "experiment/<int:pk>/edit/",
        ExperimentEditView.as_view(),
        name="experiment_edit",
    ),
    # Execution URLs
    path(
        "experiment/<int:experiment_pk>/execution/create/",
        ExecutionCreateView.as_view(),
        name="execution_create",
    ),
    path(
        "experiment/<int:experiment_pk>/execution/<int:pk>/delete/",
        ExecutionDeleteView.as_view(),
        name="execution_delete",
    ),
    # upload progress
    path("upload_progress/", upload_progress, name="upload-progress"),
]
