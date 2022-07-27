from django import template

from experiments.models import Execution, Algorithm
from experiments.models.algorithm import HyperparameterTypes

register = template.Library()


@register.simple_tag
def get_parameter_value(
    execution: Execution, algorithm: Algorithm, param_name: str
) -> HyperparameterTypes:
    value = execution.algorithm_parameters[str(algorithm.pk)][param_name]
    if isinstance(value, str):
        value = f'"{value}"'
    return value


@register.simple_tag
def default_value_of_param(
    algorithm: Algorithm, param_name: str
) -> HyperparameterTypes:
    value = algorithm.get_signature_as_dict()[param_name]
    if isinstance(value, str):
        value = f'"{value}"'
    return value
