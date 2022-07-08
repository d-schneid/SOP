import math
from abc import ABC
from typing import Dict

from backend_library.src.main.backend.task.execution.subspace.SubspaceSizeDistribution import SubspaceSizeDistribution


class UniformSubspaceDistribution(SubspaceSizeDistribution, ABC):
    def __init__(self, subspace_size_min: int, subspace_size_max: int):
        assert subspace_size_min <= subspace_size_max
        self._subspace_size_min: int = subspace_size_min
        self._subspace_size_max: int = subspace_size_max

    def get_subspace_sizes(self, requested_subspace_count: int, dataset_dimension_count: int) -> Dict[int, int]:
        assert self._subspace_size_max <= dataset_dimension_count
        size_count: int = self._subspace_size_max - self._subspace_size_min + 1
        number_of_subspaces_per_size: int = math.floor(requested_subspace_count / size_count)
        sizes_up_to_there_is_one_more_subspace: int = (requested_subspace_count % size_count) + self._subspace_size_min
        result: Dict[int, int] = dict()
        for i in range(self._subspace_size_min, self._subspace_size_max + 1):
            result[i] = number_of_subspaces_per_size + (1 if i < sizes_up_to_there_is_one_more_subspace else 0)
        return result

    def to_json(self) -> str:
        pass
