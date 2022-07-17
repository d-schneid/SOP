import math
from abc import ABC, abstractmethod
from typing import Dict


class SubspaceSizeDistribution(ABC):
    def has_enough_subspaces(self, requested_subspace_count: int,
                             dataset_dimension_count: int) -> bool:
        for k, v in self.get_subspace_counts(requested_subspace_count,
                                             dataset_dimension_count).items():
            if v > math.comb(dataset_dimension_count, k):
                return False
        return True

    @abstractmethod
    def get_subspace_counts(self, requested_subspace_count: int,
                            dataset_dimension_count: int) -> Dict[int, int]:
        """
        Calculates the number of subspaces to be generated of each size
        :param requested_subspace_count: the number of subspaces that are to be generated
        :param dataset_dimension_count: the number of dimensions the dataset has
        :return: a dictionary mapping a number of subspaces to some subspace sizes.
         The sum of all values has to be requested_subspace_count,
          0 < key <= dataset_dimension_count and 0 <= value must hold for all entries
        """
        return {}

    @abstractmethod
    def to_json(self) -> str:
        """
        Converts the important information of the SubspaceSizeDistribution into a JSON-string, so that the
        SubspaceSizeDistribution can be understood and reproduced.
        :return:
        """
        return ""
