from django.urls import path
from .views import AlgorithmUploadView, AlgorithmOverview, AlgorithmDeleteView


urlpatterns = [
    path('overview_algorithms/', AlgorithmOverview.as_view(), name="overview_algorithms"),
    path('delete_algorithm/<int:pk>', AlgorithmDeleteView.as_view(), name="delete_algorithm"),
    path('upload_algorithm/', AlgorithmUploadView.as_view(), name="upload_algorithm"),
]