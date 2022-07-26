from typing import Optional, Dict, Any

from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView

from authentication.mixins import LoginRequiredMixin
from backend.scheduler.UserRoundRobinScheduler import UserRoundRobinScheduler
from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core.Execution import Execution as BackendExecution
from backend.task.execution.subspace.RandomizedSubspaceGeneration import (
    RandomizedSubspaceGeneration,
)
from backend.task.execution.subspace.UniformSubspaceDistribution import (
    UniformSubspaceDistribution,
)
from experiments.callback import ExecutionCallbacks
from experiments.forms.create import ExecutionCreateForm
from experiments.models import Execution, Experiment
from experiments.models.execution import get_result_path
from experiments.services.execution import get_params_out_of_form
from experiments.views.generic import PostOnlyDeleteView


def schedule_backend(execution: Execution) -> Optional[Dict[str, list[str]]]:
    experiment = execution.experiment
    dataset = experiment.dataset
    algorithms = experiment.algorithms
    user = execution.experiment.user

    subspace_size_distribution = UniformSubspaceDistribution(
        subspace_size_min=execution.subspaces_min,
        subspace_size_max=execution.subspaces_max,
    )

    has_enough_subspaces = subspace_size_distribution.has_enough_subspaces(
        dataset_dimension_count=dataset.dimensions_total,
        requested_subspace_count=execution.subspace_amount,
    )
    if not has_enough_subspaces:
        return {
            "subspace_amount": [
                "Dataset does not have enough dimensions for requested subspace_amount"
            ]
        }

    subspace_generation_description = RandomizedSubspaceGeneration(
        size_distr=subspace_size_distribution,
        subspace_amount=execution.subspace_amount,
        seed=execution.subspace_generation_seed,
        dataset_total_dimension_count=dataset.dimensions_total,
    )

    parameterized_algorithms = []
    for algorithm in algorithms.all():
        parameterized_algorithms.append(
            ParameterizedAlgorithm(
                display_name=algorithm.display_name,
                path=algorithm.path,
                hyper_parameter=execution.algorithm_parameters[str(algorithm.pk)],
            )
        )
    backend_execution = BackendExecution(
        user_id=user.pk,
        task_id=execution.pk,
        task_progress_callback=ExecutionCallbacks.execution_callback,
        dataset_path=str(settings.MEDIA_ROOT / dataset.path_cleaned.path),
        result_path=get_result_path(execution),
        subspace_generation=subspace_generation_description,
        algorithms=parameterized_algorithms,
        metric_callback=ExecutionCallbacks.metric_callback,
        datapoint_count=dataset.datapoints_total,
    )
    # TODO: DO NOT do this here. Move it to AppConfig or whatever
    if UserRoundRobinScheduler._instance is None:
        UserRoundRobinScheduler()
    AlgorithmLoader.set_algorithm_root_dir(str(settings.MEDIA_ROOT / "algorithms"))

    backend_execution.schedule()
    return None


class ExecutionCreateView(
    LoginRequiredMixin, CreateView[Execution, ExecutionCreateForm]
):
    model = Execution
    template_name = "execution_create.html"
    form_class = ExecutionCreateForm
    success_url = reverse_lazy("experiment_overview")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        experiment_id = self.kwargs["experiment_pk"]
        experiment = Experiment.objects.get(pk=experiment_id)
        context.update({"experiment": experiment})
        return context

    def form_valid(self, form: ExecutionCreateForm) -> HttpResponse:
        # Get data from form
        error = False

        experiment_id = self.kwargs["experiment_pk"]
        assert experiment_id > 0
        experiment: Experiment = Experiment.objects.get(pk=experiment_id)
        assert experiment is not None
        form.instance.experiment = experiment

        # Get subspaces_min out of form and do sanity checks
        subspaces_min = form.cleaned_data["subspaces_min"]
        if subspaces_min < 0:
            form.errors.update(
                {
                    "subspaces_min": [
                        "Subspaces Min has to be an Integer greater than or equal to 0"
                    ]
                }
            )
        else:
            form.instance.subspaces_min = subspaces_min

        # Get subspaces_max out of form and do sanity checks
        subspaces_max = form.cleaned_data["subspaces_max"]
        if subspaces_max < 0:
            error = True
            form.errors.update(
                {
                    "subspaces_max": [
                        "Subspaces Max has to be greater than Subspaces Min"
                    ]
                }
            )
        if subspaces_max > experiment.dataset.dimensions_total:
            error = True
            form.errors.update(
                {
                    "subspaces_max": [
                        f"Subspaces Max has to be smaller than or equal to the dataset dimension count: {experiment.dataset.dimensions_total}"
                    ]
                }
            )
        elif 0 <= subspaces_max <= experiment.dataset.dimensions_total:
            form.instance.subspaces_max = subspaces_max

        # Get subspace_amount out of form and do sanity checks
        subspace_amount = form.cleaned_data["subspace_amount"]
        if subspace_amount <= 0:
            error = True
            form.errors.update(
                {"subspace_amount": ["Subspaces amount has to be a positive Integer"]}
            )
        else:
            form.instance.subspace_amount = subspace_amount

        # Generate algorithm_parameters out of form inputs
        dikt = get_params_out_of_form(self.request, experiment)
        assert dikt is not None
        form.instance.algorithm_parameters = dikt

        # Get subspace_generation_seed out of form and do sanity checks
        seed: Optional[int] = form.cleaned_data.get("subspace_generation_seed")
        # If the seed was not specified, it will be set to a random seed during model creation
        if seed:
            if seed < 0:
                error = True
                form.errors.update(
                    {
                        "subspace_generation_seed": [
                            "Subspaces Max has to be greater than Subspaces Min"
                        ]
                    }
                )
            else:
                form.instance.subspace_generation_seed = seed

        # Sanity check that subspaces_min must be smaller than subspaces_max
        if subspaces_min >= subspaces_max:
            error = True
            form.errors.update(
                {
                    "subspaces_max": [
                        "Subspaces Max has to be greater than Subspaces Min"
                    ]
                }
            )

        if error:
            return super(ExecutionCreateView, self).form_invalid(form)

        # we need to call super().form_valid before calling the backend, since we need
        # access to the primary key of this instance and the primary key will be set
        # on the save call in form_valid
        success_response = super(ExecutionCreateView, self).form_valid(form)
        assert form.instance.pk is not None
        assert experiment.user.pk is not None
        assert experiment.pk is not None
        assert form.instance.algorithm_parameters is not None

        errors = schedule_backend(form.instance)
        if errors:
            form.errors.update(errors)
            return super(ExecutionCreateView, self).form_invalid(form)

        return success_response


class ExecutionDuplicateView(ExecutionCreateView):
    def get_initial(self) -> Dict[str, int]:
        form = {}
        if self.request.method == "GET":
            og_execution_pk = self.kwargs["pk"]
            original = Execution.objects.get(pk=og_execution_pk)
            form["subspaces_min"] = original.subspaces_min
            form["subspaces_max"] = original.subspaces_max
            form["subspace_amount"] = original.subspace_amount
        return form

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
