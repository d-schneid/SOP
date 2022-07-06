from django.views.generic import DetailView, ListView

from authentication.mixins import LoginRequiredMixin
from experiments.models import Dataset


class DatasetDetailView(LoginRequiredMixin, DetailView):
    model = Dataset
    template_name = "experiments/dataset/dataset_detail_view.html"


class DatasetOverview(LoginRequiredMixin, ListView):
    model = Dataset
    template_name = "experiments/dataset/dataset_overview.html"

    def get_queryset(self):
        return Dataset.objects.all().filter(_user=self.request.user)
