from django import template

from experiments.models import Execution, Algorithm
from experiments.models.algorithm import HyperparameterTypes

register = template.Library()


@register.simple_tag
def get_parameter_value(
    execution: Execution, algorithm: Algorithm, param_name: str
) -> HyperparameterTypes:
    """
    A template tag to get the value of a parameter for an algorithm that was specified
    in an execution. It will wrap string in extra quotes.
    @param execution: The execution containing the hyperparameter wanted.
    @param algorithm: The algorithm used in that execution.
    @param param_name: The name of the parameter of which the specified value is wanted.
    @return: The value of the parameter specified in the execution.
    """
    value = execution.algorithm_parameters[str(algorithm.pk)][param_name]
    if isinstance(value, str):
        value = f'"{value}"'
    return value


@register.simple_tag
def default_value_of_param(
    algorithm: Algorithm, param_name: str
) -> HyperparameterTypes:
    """
    A template tag to get the default value of a parameter of an algorithm. It will wrap
    strings in extra quotes.
    @param algorithm: The algorithm containing the parameter.
    @param param_name: The name of the parameter.
    @return: The value of the parameter.
    """
    value = algorithm.get_signature_as_dict()[param_name]
    if isinstance(value, str):
        value = f'"{value}"'
    return value
