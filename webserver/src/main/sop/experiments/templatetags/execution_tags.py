from django import template

from experiments.models import Execution, Algorithm

register = template.Library()


@register.simple_tag
def default_value_of_param(algorithm: Algorithm, param_name: str):
    value = algorithm.get_signature_as_json()[param_name]
    if isinstance(value, str):
        value = f'"{value}"'
    return value
