from django import template

from experiments.models import Execution, Algorithm

register = template.Library()


def get_parameter_value(execution: Execution, algorithm: Algorithm, param_name: str):
    return execution.algorithm_parameters[str(algorithm.pk)][param_name]


def default_value_of_param(algorithm: Algorithm, param_name: str):
    value = algorithm.get_signature_as_json()[param_name]
    if isinstance(value, str):
        value = f'"{value}"'
    return value
