import base64
import math

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

    def make_subspace_array(self, full_dataset: np.array) -> np.array:
        pass
