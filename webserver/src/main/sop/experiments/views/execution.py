import json
import random

from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView

from authentication.mixins import LoginRequiredMixin
from backend.scheduler.DebugScheduler import DebugScheduler
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
from experiments.views.generic import PostOnlyDeleteView


def stub_callback(task_id: int, state: TaskState, progress: float):
    print("CALLBACK!!!!")
    print(task_id, state.name, progress)


def stub_metric_callback(execution: Execution):
    print("METRIC CALLBACK!!")
    print(
        execution.pk,
        execution.result_path,
        "created at",
        execution.creation_date,
        "finished at",
        execution.finished_date,
    )


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
                hyper_parameter=instance.algorithm_parameters,
            )
        )
    backend_execution = BackendExecution(
        user_id=user.pk,
        task_id=instance.pk,
        task_progress_callback=stub_callback,
        # TODO: use real cleaned path
        # dataset_path=dataset.path_cleaned,
        dataset_path=str(dataset.path_original),
        result_path=str(instance.result_path),
        subspace_generation=subspace_generation_description,
        algorithms=parameterized_algorithms,
        metric_callback=stub_metric_callback,
    )
    # TODO: DO NOT do this here. Move it to AppConfig or whatever
    if DebugScheduler._instance is None:
        DebugScheduler()
    # TODO: backend execution seems broken, skip for now
    # backend_execution.schedule()


class ExecutionCreateView(LoginRequiredMixin, CreateView):
    model = Execution
    template_name = "experiments/execution/execution_create.html"
    form_class = ExecutionCreateForm
    success_url = reverse_lazy("experiment_overview")

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
        algorithm_parameters: str = form.cleaned_data["algorithm_parameters"]
        assert len(algorithm_parameters) > 0
        seed: int = form.cleaned_data.get("subspace_generation_seed")
        seed: int = seed if seed is not None else random.randint(0, 10000000000)
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
        form.instance.algorithm_parameters = algorithm_parameters

        # we need to call super().form_valid before calling the backend, since we need
        # access to the primary key of this instance and the primary key will be set
        # on the save call in form_valid
        response = super(ExecutionCreateView, self).form_valid(form)
        assert form.instance.pk is not None
        assert experiment.user.pk is not None
        assert experiment.pk is not None
        form.instance.result_path = (
            settings.MEDIA_ROOT
            / "experiments"
            / ("user_" + str(experiment.user.pk))
            / ("experiment_" + str(experiment.pk))
            / ("execution_" + str(form.instance.pk))
        )
        schedule_backend(form.instance)
        return response


class ExecutionDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Execution]):
    model = Execution
    success_url = reverse_lazy("experiment_overview")
