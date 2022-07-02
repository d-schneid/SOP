import numpy as np


class Subspace:
    def __init__(self, mask: np.array):
        self._mask = mask

    @property
    def mask(self):
        return self._mask

    def get_included_dimension_count(self) -> int:
        sum = 0
        for i in np.nditer(self.mask):
            sum += i
        return sum

    def get_subspace_identifier(self) -> str:
        pass

    def get_size_of_subspace_buffer(self, full_dataset: np.array) -> int:

        pass

    def make_subspace_array(self, full_dataset: np.array, target_buffer : memoryview) -> np.array:
        pass

