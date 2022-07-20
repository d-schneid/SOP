import random
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView

from authentication.mixins import LoginRequiredMixin
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.TaskState import TaskState
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core.Execution import Execution as BackendExecution
from backend.task.execution.subspace.RandomizedSubspaceGeneration import (
    RandomizedSubspaceGeneration,
)
from backend.task.execution.subspace.UniformSubspaceDistribution import (
    UniformSubspaceDistribution,
)
from experiments.forms.create import ExecutionCreateForm
from experiments.models import Execution, Experiment
from experiments.services.execution import get_params_out_of_form
from experiments.views.generic import PostOnlyDeleteView


def stub_callback(task_id: int, state: TaskState, progress: float):
    print("CALLBACK!!!!")
    print(f"{task_id = }, {state.name = }, {progress = }")


def stub_metric_callback(execution: BackendExecution):
    print("METRIC CALLBACK!!")
    print(f"{execution.task_id = }, {execution.user_id = }, {execution.subspaces}")


def schedule_backend(instance: Execution):
    experiment = instance.experiment
    dataset = experiment.dataset
    algorithms = experiment.algorithms
    user = instance.experiment.user

    subspace_size_distribution = UniformSubspaceDistribution(
        subspace_size_min=instance.subspaces_min,
        subspace_size_max=instance.subspaces_max,
    )
    subspace_generation_description = RandomizedSubspaceGeneration(
        size_distr=subspace_size_distribution,
        subspace_amount=instance.subspace_amount,
        seed=instance.subspace_generation_seed,
        dataset_total_dimension_count=dataset.dimensions_total,
    )

    parameterized_algorithms = []
    for algorithm in algorithms.all():
        # TODO: create hyper parameters and pass them into ParameterizedAlgorithms
        parameterized_algorithms.append(
            ParameterizedAlgorithm(
                display_name=algorithm.display_name,
                path=algorithm.path,
                hyper_parameter=instance.algorithm_parameters[str(algorithm.pk)],
            )
        )
    backend_execution = BackendExecution(
        user_id=user.pk,
        task_id=instance.pk,
        task_progress_callback=stub_callback,
        dataset_path=str(settings.MEDIA_ROOT / str(dataset.path_cleaned)),
        result_path=str(settings.MEDIA_ROOT / str(instance.result_path)),
        subspace_generation=subspace_generation_description,
        algorithms=parameterized_algorithms,
        metric_callback=stub_metric_callback,
    )
    # TODO: DO NOT do this here. Move it to AppConfig or whatever
    if UserRoundRobinScheduler._instance is None:
        UserRoundRobinScheduler()
    backend_execution.schedule()


class ExecutionCreateView(
    LoginRequiredMixin, CreateView[Execution, ExecutionCreateForm]
):
    model = Execution
    template_name = "execution_create.html"
    form_class = ExecutionCreateForm
    success_url = reverse_lazy("experiment_overview")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        experiment_id = self.kwargs["experiment_pk"]
        experiment = Experiment.objects.get(pk=experiment_id)
        context.update({"experiment": experiment})
        return context

    def form_valid(self, form):
        # Get data from form
        form.instance.user = self.request.user
        experiment_id: int = self.kwargs["experiment_pk"]
        assert experiment_id > 0
        experiment: Experiment = Experiment.objects.get(pk=experiment_id)
        assert experiment is not None
        subspaces_min: int = form.cleaned_data["subspaces_min"]
        assert subspaces_min >= 0
        subspaces_max: int = form.cleaned_data["subspaces_max"]
        assert subspaces_max >= 0
        subspace_amount: int = form.cleaned_data["subspace_amount"]
        assert subspace_amount > 0
        dikt = get_params_out_of_form(self.request, experiment)
        assert dikt is not None
        form.instance.algorithm_parameters = dikt
        # TODO: add seed field to create form
        seed: int = form.cleaned_data.get("subspace_generation_seed")
        seed = seed if seed is not None else random.randint(0, 10000000000)
        if subspaces_min >= subspaces_max:
            form.errors.update(
                {
                    "subspaces_max": [
                        "Subspaces Max has to be greater than Subspaces Min"
                    ]
                }
            )
            return super(ExecutionCreateView, self).form_invalid(form)

        # save data in model
        form.instance.subspaces_min = subspaces_min
        form.instance.subspaces_max = subspaces_max
        form.instance.subspace_amount = subspace_amount
        form.instance.experiment = experiment
        form.instance.subspace_generation_seed = seed

        # we need to call super().form_valid before calling the backend, since we need
        # access to the primary key of this instance and the primary key will be set
        # on the save call in form_valid
        response = super(ExecutionCreateView, self).form_valid(form)
        assert form.instance.pk is not None
        assert experiment.user.pk is not None
        assert experiment.pk is not None
        assert form.instance.algorithm_parameters is not None
        # TODO: WARNING! This path will not be saved in the model, as the model isn't saved
        # after this declaration. It is used though in the schedule_backend() function to
        # tell the backend where to save the result. We have to set this again when we have
        # a result in the filesystem to put a valid path into the model.
        # Maybe move this path calculation into schedule_backend() to remove confusion about
        # this being an attribute of the model, but not being accessible later
        form.instance.result_path = (
            settings.MEDIA_ROOT
            / "experiments"
            / ("user_" + str(experiment.user.pk))
            / ("experiment_" + str(experiment.pk))
            / ("execution_" + str(form.instance.pk))
        )
        # TODO:start scheduling as soon as DatasetCleaning on Dataset upload is implemented
        # schedule_backend(form.instance)
        return response


class ExecutionDuplicateView(ExecutionCreateView):
    def get_initial(self):
        form = {}
        if self.request.method == "GET":
            og_execution_pk = self.kwargs["pk"]
            original = Execution.objects.get(pk=og_execution_pk)
            form["subspaces_min"] = original.subspaces_min
            form["subspaces_max"] = original.subspaces_max
            form["subspace_amount"] = original.subspace_amount
        return form

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["original"] = Execution.objects.get(pk=self.kwargs["pk"])
        return context


class ExecutionDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Execution]):
    model = Execution
    success_url = reverse_lazy("experiment_overview")


def download_execution_result(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "GET":
        execution: Optional[Execution] = Execution.objects.filter(pk=pk).first()
        if execution is None:
            return HttpResponseRedirect(reverse_lazy("experiment_overview"))

        file_name = "result.zip"
        with execution.result_path as file:
            response = HttpResponse(file.read())
            response["Content-Type"] = "text/plain"
            response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response
    else:
        assert request.method in ("POST", "PUT")
        return HttpResponseRedirect(reverse_lazy("experiment_overview"))
