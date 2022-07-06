from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, \
    UpdateView, DetailView

from authentication.mixins import LoginRequiredMixin
from experiments.forms.create import AlgorithmUploadForm
from experiments.forms.edit import AlgorithmEditForm
from experiments.models import Algorithm


class AlgorithmOverview(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'next'

    model = Algorithm
    template_name = 'algorithm_overview.html'


class AlgorithmUploadView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'next'

    model = Algorithm
    form_class = AlgorithmUploadForm
    template_name = 'algorithm_upload.html'
    success_url = reverse_lazy('algorithm_overview')

    def form_valid(self, form) -> HttpResponseRedirect:
        form.instance.user = self.request.user
        return super(AlgorithmUploadView, self).form_valid(form)


class AlgorithmDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    redirect_field_name = 'next'

    model = Algorithm
    template_name = 'algorithm_delete.html'
    success_url = reverse_lazy('algorithm_overview')


class AlgorithmEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'next'

    model = Algorithm
    form_class = AlgorithmEditForm
    template_name = 'algorithm_edit.html'
    success_url = reverse_lazy('algorithm_overview')


class AlgorithmDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'next'

    model = Algorithm
    # template_name =
