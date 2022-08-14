from __future__ import annotations

import json
from typing import Optional, Dict, Any, List

from django.conf import settings
from django.contrib import messages
from django.db.models import QuerySet
from django.http import (
    HttpRequest,
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseServerError,
)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from authentication.mixins import LoginRequiredMixin
from backend.task.TaskState import TaskState
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
from experiments.models import Execution, Experiment, Algorithm
from experiments.models.execution import get_result_path, ExecutionStatus
from experiments.services.execution import get_params_out_of_form, get_execution_result
from experiments.views.generic import PostOnlyDeleteView


def schedule_backend(execution: Execution) -> Optional[Dict[str, list[str]]]:
    """
    Schedules a backend task that will start the calculations of the given execution.
    @param execution: The execution for which the calculation should be started.
    @return: If the scheduling is successful and all parameters of the given execution
    are valid, it will return None. If errors occur, it will return a dictionary that
    contains the names of the execution model fields that resulted in the error as keys
    and an error message as the value.
    """
    experiment = execution.experiment
    dataset = experiment.dataset
    algorithms: QuerySet[Algorithm] = experiment.algorithms.all()
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
    for algorithm in algorithms:
        parameterized_algorithms.append(
            ParameterizedAlgorithm(
                display_name=algorithm.display_name,
                path=algorithm.path.path,
                hyper_parameter=execution.algorithm_parameters[str(algorithm.pk)],
            )
        )
    backend_execution = BackendExecution(
        user_id=user.pk,
        task_id=execution.pk,
        task_progress_callback=ExecutionCallbacks.execution_callback,
        dataset_path=str(settings.MEDIA_ROOT / dataset.path_cleaned.path),
        result_path=get_result_path(execution),
        datapoint_count=dataset.datapoints_total,
        subspace_generation=subspace_generation_description,
        algorithms=parameterized_algorithms,
        metric_callback=ExecutionCallbacks.metric_callback,
    )

    backend_execution.schedule()
    return None


def generate_hyperparameter_error_message(dikt: Dict[str, List[str]]) -> str:
    """
    Create an error message string out of a given errors dictionary. This method will
    most likely be removed when errors are displayed by django messages.
    @param dikt: The errors dictionary in the form {'field_name' : 'error_message'}
    @return: The error message string.
    """
    msg = ""
    for key, errors in dikt.items():
        algo_pk, param_name = key.split("_", maxsplit=1)
        algorithm = Algorithm.objects.get(pk=algo_pk)
        msg += f"{algorithm.display_name}.{param_name}: "
        msg += "\n".join(errors)
        msg += "\n"
    return msg


class ExecutionCreateView(
    LoginRequiredMixin, CreateView[Execution, ExecutionCreateForm]
):
    """
    A view to create an execution for a experiment. It uses the ExecutionCreateForm for
    displaying widgets for the fields a user has to enter and dynamically get fields
    for hyperparameters of all algorithms in the experiment out of the form.
    When the form is valid a backend task for the calculation will be scheduled.
    """

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
            messages.error(
                self.request,
                "Subspaces Min has to be an Integer greater than or equal to 0.",
            )
        else:
            form.instance.subspaces_min = subspaces_min

        # Get subspaces_max out of form and do sanity checks
        subspaces_max = form.cleaned_data["subspaces_max"]
        if subspaces_max < 0:
            messages.error(
                self.request,
                "Subspaces Max has to be an Integer greater than or equal to 0.",
            )
            error = True
        if subspaces_max > experiment.dataset.dimensions_total:
            messages.error(
                self.request,
                f"Subspaces Max has to be smaller than or equal to the dataset dimension count: {experiment.dataset.dimensions_total}.",
            )
            error = True
        elif 0 <= subspaces_max <= experiment.dataset.dimensions_total:
            form.instance.subspaces_max = subspaces_max

        # Get subspace_amount out of form and do sanity checks
        subspace_amount = form.cleaned_data["subspace_amount"]
        if subspace_amount <= 0:
            messages.error(
                self.request, "Subspace amount has to be a positive Integer."
            )
            error = True
        else:
            form.instance.subspace_amount = subspace_amount

        # Generate algorithm_parameters out of form inputs
        success, dikt = get_params_out_of_form(self.request, experiment)
        if success:
            form.instance.algorithm_parameters = dikt
        else:
            error = True
            messages.error(self.request, generate_hyperparameter_error_message(dikt))

        # Get subspace_generation_seed out of form and do sanity checks
        seed: Optional[int] = form.cleaned_data.get("subspace_generation_seed")
        # If the seed was not specified, it will be set to a random seed during model creation
        if seed:
            if seed < 0:
                messages.error(
                    self.request, f"Seed has to be greater than 0. (is: {seed})."
                )
                error = True
            else:
                form.instance.subspace_generation_seed = seed

        # Sanity check that subspaces_min must be smaller than subspaces_max
        if subspaces_min > subspaces_max:
            messages.error(
                self.request,
                "Subspaces Max has to be greater than or equal to Subspaces Min.",
            )
            error = True

        # set status of execution to running
        form.instance.status = TaskState.RUNNING.name

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
    """
    A view to duplicate an execution. This will act just like the ExecutionCreateView
    except that it adds default values for the subspace information to the form and the
    original execution to the context, so that the template can enter default values for
    the hyperparameters.
    """

    def get_initial(self) -> Dict[str, int]:
        form = {}
        if self.request.method == "GET":
            og_execution_pk = self.kwargs["pk"]
            original = Execution.objects.get(pk=og_execution_pk)
            form["subspaces_min"] = original.subspaces_min
            form["subspaces_max"] = original.subspaces_max
            form["subspace_amount"] = original.subspace_amount
            form["subspace_generation_seed"] = original.subspace_generation_seed
        return form

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["original"] = Execution.objects.get(pk=self.kwargs["pk"])
        return context


class ExecutionDeleteView(LoginRequiredMixin, PostOnlyDeleteView[Execution]):
    """
    A view to delete an execution model. It inherits form PostOnlyDeleteView, so it is
    only accessible via POST requests.
    """

    model = Execution
    success_url = reverse_lazy("experiment_overview")


def download_execution_result(
    request: HttpRequest, experiment_pk: int, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    """
    A function view that will download an execution result. This view asserts that the
    execution has results located at the path in the result_path attribute of the
    execution. Accessing this view with an unfinished execution will redirect to the
    experiment overview.

    @param request: The HTTPRequest, this will be given by django.
    @param experiment_pk: The primary key of the experiment of the execution.
    @param pk: The primary key of the execution itself.
    @return: If the request is valid and the given primary keys are valid, this returns
    a HTTPResponse with the result download. If the given primary keys are invalid, this
    return a redirect to the experiment overview. If this view is accessed with a POST
    request, it will return None.
    """
    if request.method == "GET":
        execution: Optional[Execution] = Execution.objects.filter(pk=pk).first()
        if execution is None:
            return HttpResponseRedirect(reverse_lazy("experiment_overview"))
        return get_execution_result(execution)
    else:
        assert request.method in ("POST", "PUT")
        return None


def download_execution_result_admin(
    request: HttpRequest, pk: int
) -> Optional[HttpResponse | HttpResponseRedirect]:
    """
    A function view that will download an execution result. This view asserts that the
    execution has results located at the path in the result_path attribute of the
    execution. Accessing this view with an unfinished execution will result in
    unexpected behaviour.

    @param request: The HTTPRequest, this will be given by django.
    @param pk: The primary key of the execution.
    @return: If the request is valid and the given primary key is valid, this returns
    a HTTPResponse with the result download. If the given primary key is invalid, this
    return a redirect to the change list of the Execution model instances in the admin
    interface. If this view is accessed with a POST request, it will return None.
    """
    if request.method == "GET":
        execution: Optional[Execution] = Execution.objects.filter(pk=pk).first()
        if execution is None:
            return HttpResponseRedirect(
                reverse_lazy("admin:experiments_execution_changelist")
            )
        return get_execution_result(execution)
    else:
        assert request.method in ("POST", "PUT")
        return None


def get_execution_progress(request: HttpRequest) -> HttpResponse:
    """
    A function view that will return a HTTPResponse with json data containing the
    progress and status of an execution. The primary key of the wanted execution can
    be given via the 'execution_pk' argument in the url or in the META of the request.

    @param request: The HTTPRequest, this will be given by django.
    @return: If no primary key is given, this will return a ServerError with an error
    message.
    If a primary key is given and it is invalid, it will return empty json
    data.
    If a primary key is given and it is valid, it will return the progress and
    status of the execution in this form:
    {
       'execution_pk': pk_int,
       'progress': progress_float,
       'status': status_string
    }
    """
    pk = 0
    if "execution_pk" in request.GET:
        pk = request.GET["execution_pk"]
    elif "execution_pk" in request.META:
        pk = request.META["execution_pk"]
    if pk:
        execution: Optional[Execution] = Execution.objects.filter(pk=pk).first()
        data: Dict[str, Any] = {}
        if execution is not None:
            data["is_running"] = execution.is_running
            data["has_result"] = execution.has_result
            data["progress"] = execution.progress
            data["status"] = execution.status
            data["experiment_pk"] = execution.experiment.pk

        return HttpResponse(json.dumps(data))

    else:
        return HttpResponseServerError(
            "Server Error: You must provide execution_pk header or query param."
        )


def restart_execution(
    request: HttpRequest, experiment_pk: int, pk: int
) -> HttpResponse:
    """
    A view that can be accessed in any way (GET or POST). When accessed, it will restart
    the execution specified by the given primary key.

    @param request: The HttpRequest, this will be given by django.
    @param experiment_pk: The primary key of the experiment of the execution.
    @param pk: The primary key of the execution itself.
    @return: A redirect to the experiment overview.
    """
    execution = Execution.objects.filter(pk=pk).first()
    if execution is not None:
        execution.status = ExecutionStatus.RUNNING.name
        execution.progress = 0.0
        execution.save()
        schedule_backend(execution)
    return HttpResponseRedirect(reverse_lazy("experiment_overview"))
