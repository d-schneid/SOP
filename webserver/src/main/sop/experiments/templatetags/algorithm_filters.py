from django import template

from experiments.models.managers import AlgorithmQuerySet
from experiments.models import Algorithm

register = template.Library()


@register.filter
def in_group(
    algorithms: AlgorithmQuerySet, group: Algorithm.AlgorithmGroup
) -> AlgorithmQuerySet:
    """
    A filter to filter for algorithms of the given group.
    @param algorithms: The algorithms to filter for.
    @param group: The group to filter for.
    @return: The algorithms that belong to the given group.
    """
    return algorithms.filter(group=group)
