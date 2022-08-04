from __future__ import annotations

from typing import Dict, Tuple, List

from django.http import HttpRequest, HttpResponse

from experiments.models import Experiment, Execution
from experiments.models.algorithm import HyperparameterTypes


def get_params_out_of_form(
    request: HttpRequest, experiment: Experiment
) -> Tuple[bool, Dict[str, List[str]] | Dict[str, Dict[str, HyperparameterTypes]]]:
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

    dikt: Dict[str, Dict[str, HyperparameterTypes]] = dict()
    errors: Dict[str, List[str]] = dict()

    for algo in experiment.algorithms.all():
        algo_dict: Dict[str, HyperparameterTypes] = dict()

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

        # Add the algorithms specific dictionary to the global dictionary and go on to the next algorithm
        dikt.update({str(algo.pk): algo_dict})

    if errors:
        return False, errors
    else:
        return True, dikt


def get_execution_result(execution: Execution) -> HttpResponse:
    file_name = "result.zip"
    with execution.result_path as file:
        response = HttpResponse(file.read())
        response["Content-Type"] = "text/plain"
        response["Content-Disposition"] = f"attachment; filename={file_name}"
    return response
