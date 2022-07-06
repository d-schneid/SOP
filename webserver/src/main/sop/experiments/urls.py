from django.urls import path

from .views.algorithm import AlgorithmEditView, AlgorithmUploadView, \
    AlgorithmDeleteView, AlgorithmOverview
from experiments.views.dataset import DatasetOverview, DatasetDetailView

urlpatterns = [
    path('algorithm/overview/', AlgorithmOverview.as_view(),
         name="algorithm_overview"),
    path('algorithm/<int:pk>/delete/', AlgorithmDeleteView.as_view(),
         name="algorithm_delete"),
    path('algorithm/<int:pk>/edit/', AlgorithmEditView.as_view(),
         name="algorithm_edit"),
    path('algorithm/upload/', AlgorithmUploadView.as_view(),
         name="algorithm_upload"),

    # Dataset URLs
    path('dataset/overview/', DatasetOverview.as_view(), name="dataset_overview"),
    path('dataset/<int:pk>/', DatasetDetailView.as_view(), name="dataset_detail_view")
]
