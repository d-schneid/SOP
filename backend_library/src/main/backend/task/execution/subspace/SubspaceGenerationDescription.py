from collections.abc import Iterable
from abc import ABC, abstractmethod

from backend.task.execution.subspace.Subspace import Subspace


class SubspaceGenerationDescription(ABC):
    @abstractmethod
    def generate(self) -> Iterable[Subspace]:
        """
        Generates the Subspaces deterministically. \n
        :return: The generated Subspaces.
        """
        return iter([])

    @abstractmethod
    def to_json(self) -> str:
        """
        Converts the important information of the SubspaceGenerationDescription into a JSON-string, so that the
        Subspace generation can be understood and reproduced. \n
        :return: the JSON-string
        """
        return ""
