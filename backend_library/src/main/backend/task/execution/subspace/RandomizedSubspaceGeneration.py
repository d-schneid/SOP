import random
import string
from typing import Iterable

import numpy as np

from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace
from backend_library.src.main.backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend_library.src.main.backend.task.execution.subspace.SubspaceSizeDistribution import SubspaceSizeDistribution


class RandomizedSubspaceGeneration(SubspaceGenerationDescription):
    def __init__(self, size_distr: SubspaceSizeDistribution, subspace_amount: int, seed: int):
        self._rnd = np.random.Generator(np.random.bit_generator.PCG64(seed))
        self._size_distr = size_distr
        self._subspace_amount = subspace_amount

    def to_json(self) -> string:
        pass

    def generate(self, dataset_total_dimension_count: int) -> Iterable[Subspace]:
        size_counts = self._size_distr.get_subspace_sizes(self._subspace_amount, dataset_total_dimension_count)
        result = list()
        for k, v in size_counts:
            result.extend(self._generate_subspaces_of_size(k, v, dataset_total_dimension_count))
        return result

    def _generate_subspaces_of_size(self, size: int, count: int, ds_dim_count: int) -> Iterable[Subspace]:
        result = list()
        result_bytes = list()
        RandomizedSubspaceGeneration._ensure_enough_subspaces(size, count, ds_dim_count)
        current_mask = np.concatenate((np.repeat(True, size), np.repeat(False, ds_dim_count - size)))
        while len(result) < count:
            self._rnd.shuffle(current_mask)
            current_mask_bytes = np.packbits(current_mask).tobytes()
            if current_mask_bytes not in result_bytes:
                result_bytes.append(current_mask_bytes)
                result.append(Subspace(current_mask.copy()))
        return result

    @staticmethod
    def _ensure_enough_subspaces(size: int, count: int, ds_dim_count: int) -> None:
        pass