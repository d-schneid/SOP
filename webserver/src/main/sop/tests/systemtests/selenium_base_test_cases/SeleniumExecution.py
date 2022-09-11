from typing import List


class SeleniumExecution:
    def __init__(
        self,
        subspace_amount: str,
        subspaces_min: str,
        subspaces_max: str,
        subspace_gen_seed: str,
        algos: List[dict],
    ):

        # NOTE: the type of e.g. subspace_amount was purposefully chosen as integer,
        # so that wrong data entry can be simulated

        self._subspace_amount = subspace_amount
        self._subspaces_min = subspaces_min
        self._subspaces_max = subspaces_max
        self._subspace_gen_seed = subspace_gen_seed
        self._algos = algos

    @property
    def subspace_amount(self) -> str:
        return self._subspace_amount

    @property
    def subspaces_min(self) -> str:
        return self._subspaces_min

    @property
    def subspace_max(self) -> str:
        return self._subspaces_max

    @property
    def subspace_gen_seed(self) -> str:
        return self._subspace_gen_seed

    @property
    def algos(self) -> List[dict]:
        return self._algos
