from __future__ import annotations

from typing import Optional, Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse

from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm
from backend.task.execution.core.Execution import Execution as BackendExecution
from backend.task.execution.subspace.RandomizedSubspaceGeneration import (
    RandomizedSubspaceGeneration,
)
from backend.task.execution.subspace.UniformSubspaceDistribution import (
    UniformSubspaceDistribution,
)
from experiments.callback import ExecutionCallbacks
from experiments.models import Experiment, Execution
from experiments.models.algorithm import HyperparameterTypes, Algorithm
from experiments.models.execution import get_result_path


def get_params_out_of_form(
    request: HttpRequest, experiment: Experiment
) -> tuple[bool, dict[str, list[str]] | dict[str, dict[str, HyperparameterTypes]]]:
    """
    Extracts the hyperparameters specified in the ExecutionCreateForm.
    @param request: The HttpRequest containing the fields of the hyperparameters.
    @param experiment: The experiment of the created execution.
    @return: A tuple containing a success boolean and a result dictionary.
    If the boolean is True, the extraction was successful and the result dictionary
    contains parameter name to parameter value mappings for each algorithm in the
    experiment.
    If the boolean is False, the extraction was not successful and the dict contains
    a mapping from the hyperparameter form_field which caused an error to an error
    message.
    """
    dikt: dict[str, dict[str, HyperparameterTypes]] = dict()
    errors: dict[str, list[str]] = dict()

    for algo in experiment.algorithms.all():
        algo_dict: dict[str, HyperparameterTypes] = dict()

        for param_name in algo.get_signature_as_dict().keys():
            form_key = f"{algo.pk}_{param_name}"
            form_value = request.POST[form_key]

            assert isinstance(
                form_value, str
            ), "POST request arguments have to be strings"

            try:
                evaluated_value = eval(form_value)
                # Add this param to the algorithms specific dictionary
                algo_dict.update({str(param_name): evaluated_value})
            except SyntaxError as e:
                errors.update({form_key: [e.msg]})
            except NameError:
                errors.update({form_key: ["strings must be wrapped in quotes"]})

        # Add the algorithms specific dictionary to the global dictionary
        # and go on to the next algorithm
        dikt.update({str(algo.pk): algo_dict})

    if errors:
        return False, errors
    else:
        return True, dikt


def get_download_http_response(data: Any, file_name: str) -> HttpResponse:
    response = HttpResponse(data)
    response["Content-Type"] = "text/plain"
    response["Content-Disposition"] = f"attachment; filename={file_name}"
    return response


def get_execution_result(execution: Execution) -> HttpResponse:
    """
    Generates a HttpResponse for a download with the content of the result file of the
    given execution.
    @param execution: The execution of which the result file shall be downloaded.
    @return: A HttpResponse with the download.
    """
    file_name = "result.zip"
    with execution.result_path as file:
        return get_download_http_response(file.read(), file_name)


def schedule_backend(execution: Execution) -> Optional[dict[str, list[str]]]:
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
