import itertools
import math
from abc import ABC
from collections.abc import Iterable

import numpy as np

from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.subspace.SubspaceGenerationDescription import \
    SubspaceGenerationDescription
from backend.task.execution.subspace.SubspaceSizeDistribution import \
    SubspaceSizeDistribution


class RandomizedSubspaceGeneration(SubspaceGenerationDescription, ABC):
    """Class for randomly generating Subspaces
    of a size determined by a SubspaceSizeDistribution"""

    def __init__(self, size_distr: SubspaceSizeDistribution,
                 dataset_total_dimension_count: int, subspace_amount: int, seed: int):
        """
        Creates a new RandomizedSubspaceGeneration
        :param size_distr: the distribution of subspace sizes to use
        :param dataset_total_dimension_count: the number of dimensions the dataset has
        :param subspace_amount: the number of subspaces to use
        :param seed: the seed to generate those subspaces with
        """
        self.__rnd: np.random.Generator = np.random.Generator(np.random.PCG64(seed))
        self.__ds_dim_count = dataset_total_dimension_count
        self.__size_distr: SubspaceSizeDistribution = size_distr
        self.__subspace_amount: int = subspace_amount
        self.__seed: int = seed
        assert size_distr.has_enough_subspaces(subspace_amount,
                                               dataset_total_dimension_count), \
            "too many subspaces were requested"

    def to_json(self) -> dict[str, object]:
        return {"size_distr": self.__size_distr.to_json(), "seed": self.__seed,
                "subspace_amount": self.__subspace_amount,
                "dataset_dimension_count": self.__ds_dim_count}

    def generate(self) -> list[Subspace]:
        """
        Generates the subspaces to be used
        :return: a list of subspaces to be used
        """
        size_counts: dict[int, int] = self.__size_distr.get_subspace_counts(
            self.__subspace_amount, self.__ds_dim_count)
        result: list[Subspace] = list()
        for k, v in size_counts.items():
            result.extend(self.__generate_subspaces_of_size(k, v))
        return result

    def __generate_subspace_bits(self, size: int, count: int) -> set[bytes]:
        """generates a set of #count bytes objects,
         each of them containing #size ones,
         only the first #self.__ds_dim_count bits will be used.
         Takes exponential time as count approaches comb(self.__ds_dim_count, size)"""
        result_bytes: set[bytes] = set()
        current_mask: np.array = np.concatenate(
            (np.repeat(True, size), np.repeat(False, self.__ds_dim_count - size)))
        while len(result_bytes) < count:
            self.__rnd.shuffle(current_mask)
            current_mask_bytes: bytes = np.packbits(current_mask).tobytes()
            if current_mask_bytes not in result_bytes:
                result_bytes.add(current_mask_bytes)
        return result_bytes

    def __generate_subspaces_of_size(self, ss_size: int, count: int) \
            -> Iterable[Subspace]:
        """
        Generates the subspaces needed of a given size
        :param ss_size: the size of the subspaces to generate
        :param count: the number of subspaces to generate
        :return: an iterable of subspaces of that size
        """
        if (count / math.comb(self.__ds_dim_count, ss_size)) > 0.5:
            ss_bits = self.__generate_dense_subspace_bits(ss_size, count)
        else:
            ss_bits = self.__generate_subspace_bits(ss_size, count)
        ss = map(lambda b: self.__subspace_from_bytes(b, self.__ds_dim_count), ss_bits)
        return ss

    @staticmethod
    def __subspace_from_bytes(b: bytes, ds_dim_count: int) -> Subspace:
        """creates a subspace for dataset of specified size from a bytes object"""
        packed_bits = np.frombuffer(b, dtype=np.dtype('u1'))
        unpacked_bits = np.unpackbits(packed_bits, count=ds_dim_count)
        unpacked_bits.dtype = np.dtype("?")
        return Subspace(unpacked_bits)

    def __generate_dense_subspace_bits(self, ss_size: int, count: int):
        """Performance improved subspace generation when more than 50% of the subspaces
         available in a given size are to be selected,
          normal generation would take exponentially long in such cases."""
        # Works by generating self.__subspace_amount - count subspace bits
        # and then returning all that were not in that sample
        ss_bits = self.__generate_subspace_bits(ss_size, self.__subspace_amount - count)
        # one could check in the future if ss_size/self.ds_dim_count>0.5 is given
        # and then remove dims instead of adding them, would improve constant factors
        # of this generation algorithm, but I don't see the need for that
        combs = itertools.combinations(range(self.__ds_dim_count), ss_size)
        for comb in combs:
            comb_array = np.full(self.__ds_dim_count, False)
            comb_array[np.array(comb)] = True
            ss_bytes = np.packbits(comb_array).tobytes()
            if ss_bytes not in ss_bits:
                yield ss_bytes
