from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView

from experiments.forms import UploadAlgorithmForm
from experiments.models import Algorithm


class AlgorithmOverview(ListView):
    model = Algorithm
    template_name = 'algorithm_overview.html'


class AlgorithmUploadView(CreateView):
    model = Algorithm
    form_class = UploadAlgorithmForm
    template_name = 'algorithm_upload.html'

    def form_valid(self, form) -> HttpResponseRedirect:
        form.instance.user = self.request.user
        return super(AlgorithmUploadView, self).form_valid(form)


class AlgorithmDeleteView(DeleteView):
    model = Algorithm
    template_name = 'algorithm_delete.html'
    success_url = reverse_lazy('algorithm_overview')


class AlgorithmEditView(UpdateView):
    model = Algorithm
    fields = ['_name', '_description']
    template_name = 'algorithm_edit.html'
    success_url = reverse_lazy('algorithm_overview')
