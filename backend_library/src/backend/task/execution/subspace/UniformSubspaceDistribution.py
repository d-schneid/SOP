import math
from abc import ABC

from backend.task.execution.subspace.SubspaceSizeDistribution \
    import SubspaceSizeDistribution


class UniformSubspaceDistribution(SubspaceSizeDistribution, ABC):
    """A SubspaceSizeDistribution where there is almost the same number of Subspaces
     for each Size in a range"""

    def __init__(self, subspace_size_min: int, subspace_size_max: int):
        """
        Creates a new UniformSubspaceDistribution
        :param subspace_size_min:  The minimum Size of Subspaces to create, inclusive
        :param subspace_size_max:  The maximum Size of Subspaces to create, inclusive
        :raises AssertionError when 0 < size_min <= size_max does not hold
        """
        assert 0 < subspace_size_min <= subspace_size_max
        self._subspace_size_min: int = subspace_size_min
        self._subspace_size_max: int = subspace_size_max

    def get_subspace_counts(self, requested_subspace_count: int,
                            dataset_dimension_count: int) -> dict[int, int]:
        """
        Calculates how many subspaces there are of each Size
        :param requested_subspace_count: How may subspaces are needed
        :param dataset_dimension_count: How many dimensions the dataset has
        :raises AssertionError when size_max <= dataset_dimension_count or
        requested_subspace_count > 0 does not hold
        """
        assert self._subspace_size_max <= dataset_dimension_count
        assert requested_subspace_count > 0
        size_count: int = self._subspace_size_max - self._subspace_size_min + 1
        number_of_subspaces_per_size: int = \
            math.floor(requested_subspace_count / size_count)
        sizes_with_one_more_subspace: int = \
            (requested_subspace_count % size_count) + self._subspace_size_min
        result: dict[int, int] = dict()
        for i in range(self._subspace_size_min, self._subspace_size_max + 1):
            additional_subspaces = (1 if i < sizes_with_one_more_subspace else 0)
            result[i] = number_of_subspaces_per_size + additional_subspaces
        return result

    def to_json(self) -> dict[str, object]:
        return {"subspace_size_min": self._subspace_size_min,
                "subspace_size_max": self._subspace_size_max}
