import random
import string
from abc import ABC
from typing import Iterable, Dict, List

import numpy as np

from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend.task.execution.subspace.SubspaceSizeDistribution import SubspaceSizeDistribution


class RandomizedSubspaceGeneration(SubspaceGenerationDescription, ABC):
    def __init__(self, size_distr: SubspaceSizeDistribution, dataset_total_dimension_count: int, subspace_amount: int,
                 seed: int):
        self.__rnd: np.random.Generator = np.random.Generator(np.random.PCG64(seed))
        self.__ds_dim_count = dataset_total_dimension_count
        self.__size_distr: SubspaceSizeDistribution = size_distr
        self.__subspace_amount: int = subspace_amount

    def to_json(self) -> string:
        pass

    def generate(self) -> Iterable[Subspace]:
        size_counts: Dict[int, int] = self.__size_distr.get_subspace_sizes(self.__subspace_amount, self.__ds_dim_count)
        result: List[Subspace] = list()
        for k, v in size_counts.items():
            result.extend(self.__generate_subspaces_of_size(k, v))
        return result

    def __generate_subspaces_of_size(self, size: int, count: int) -> Iterable[Subspace]:
        result: List[Subspace] = list()
        result_bytes: List[bytes] = list()
        RandomizedSubspaceGeneration.__ensure_enough_subspaces(size, count, self.__ds_dim_count)
        current_mask: np.array = np.concatenate((np.repeat(True, size), np.repeat(False, self.__ds_dim_count - size)))
        while len(result) < count:
            self.__rnd.shuffle(current_mask)
            current_mask_bytes: bytes = np.packbits(current_mask).tobytes()
            if current_mask_bytes not in result_bytes:
                result_bytes.append(current_mask_bytes)
                result.append(Subspace(current_mask.copy()))
        return result

    @staticmethod
    def __ensure_enough_subspaces(size: int, count: int, ds_dim_count: int) -> None:
        pass
