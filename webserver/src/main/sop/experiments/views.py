from django.views.generic import CreateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from experiments.models import Algorithm
from .forms import UploadAlgorithmForm


class AlgorithmOverview(ListView):
    model = Algorithm
    template_name = 'test_overview_algorithms.html'

class AlgorithmUploadView(CreateView):
    model = Algorithm
    form_class = UploadAlgorithmForm
    template_name = 'test_upload_algorithm.html'

    def form_valid(self, form) -> HttpResponseRedirect:
        form.instance.user = self.request.user
        return super(AlgorithmUploadView, self).form_valid(form)

class AlgorithmDeleteView(DeleteView):
    model = Algorithm
    template_name = 'test_delete_algorithm.html'
    success_url = reverse_lazy('overview_algorithms')