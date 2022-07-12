import base64
import math
from multiprocessing.shared_memory import SharedMemory

import numpy as np


class Subspace:
    """Represents a Subspace of a n-dimensional Space"""
    def __init__(self, mask: np.array):
        self._mask = mask

    @property
    def mask(self) -> np.array:
        """A numpy array storing for each dimension of the Space,
         whether it is included in the Subspace"""
        return self._mask

    def get_included_dimension_count(self) -> int:
        """Counts the dimensions included in the Subspace"""
        counter = 0
        for i in np.nditer(self.mask):
            counter += i
        return counter

    def get_subspace_identifier(self) -> str:
        """
        Determines the subspace-identifier of this Subspace
        :return: A non-padded b64-url encoded version of the mask
        """
        encoded_bytes = base64.urlsafe_b64encode(np.packbits(self.mask).tobytes())
        return bytes.decode(encoded_bytes)[:math.ceil(self.mask.size / 6)]

    def get_size_of_subspace_buffer(self, full_dataset: np.ndarray) -> int:
        """Calculates how bug a buffer for an numpy array would have to be
        to fit this Subspace
        :param full_dataset the dataset for which to run this calculation"""
        return full_dataset.shape[1] * full_dataset.itemsize * self.mask.size

    def make_subspace_array(self, full_dataset: np.ndarray, target_shm: SharedMemory) \
            -> np.ndarray:
        """Builds an ndarray in the specified SharedMemory,
         containing the Subspace of the dataset"""
        shape = (self.mask.size, full_dataset.shape[1])
        result = np.ndarray(shape, full_dataset.dtype, buffer=target_shm.buf)
        result[:] = full_dataset[:, self._mask]
        return result
