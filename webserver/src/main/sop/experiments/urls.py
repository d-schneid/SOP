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
    download_cleaned_dataset,
    download_uncleaned_dataset,
    dataset_status_view,
)
from experiments.views.execution import (
    ExecutionCreateView,
    ExecutionDeleteView,
    ExecutionDuplicateView,
    download_execution_result, get_execution_progress, restart_execution,
)
from experiments.views.experiment import (
    ExperimentOverview,
    ExperimentCreateView,
    ExperimentDeleteView,
    ExperimentEditView,
    ExperimentDuplicateView,
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
    path(
        "dataset/<int:pk>/download_cleaned/",
        download_cleaned_dataset,
        name="dataset_download_cleaned",
    ),
    path(
        "dataset/<int:pk>/download_uncleaned/",
        download_uncleaned_dataset,
        name="dataset_download_uncleaned",
    ),
    path("dataset-status/", dataset_status_view, name="dataset_status"),
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
    path(
        "experiment/<int:pk>/duplicate/",
        ExperimentDuplicateView.as_view(),
        name="experiment_duplicate",
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
    path(
        "experiment/<int:experiment_pk>/execution/<int:pk>/duplicate/",
        ExecutionDuplicateView.as_view(),
        name="execution_duplicate",
    ),
    path(
        "experiment/<int:experiment_pk>/execution/<int:pk>/download_results/",
        download_execution_result,
        name="execution_download_result",
    ),
    path(
        "experiment/<int:experiment_pk>/execution/<int:pk>/restart/",
        restart_execution,
        name="execution_restart",
    ),
    path("execution_progress/", get_execution_progress, name="execution_progress"),
    # upload progress
    path("upload_progress/", upload_progress, name="upload-progress"),
]
