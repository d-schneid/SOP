import base64
import math
from multiprocessing.shared_memory import SharedMemory

import numpy as np


class Subspace:
    def __init__(self, mask: np.array):
        self._mask = mask

    @property
    def mask(self) -> np.array:
        return self._mask

    def get_included_dimension_count(self) -> int:
        counter = 0
        for i in np.nditer(self.mask):
            counter += i
        return counter

    def get_subspace_identifier(self) -> str:
        encoded_bytes = base64.urlsafe_b64encode(np.packbits(self.mask).tobytes())
        return bytes.decode(encoded_bytes)[:math.ceil(self.mask.size / 6)]

    def get_size_of_subspace_buffer(self, full_dataset: np.ndarray) -> int:
        return full_dataset.shape[1] * full_dataset.itemsize * self.mask.size

    def make_subspace_array(self, full_dataset: np.ndarray, target_shm: SharedMemory) -> np.ndarray:
        result = np.ndarray((self.mask.size, full_dataset.shape[1]), full_dataset.dtype, buffer=target_shm.buf)
        result[:] = full_dataset[:, self._mask]
        return result
