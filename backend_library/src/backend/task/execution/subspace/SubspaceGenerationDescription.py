from abc import ABC, abstractmethod

from backend.JsonSerializable import JsonSerializable
from backend.task.execution.subspace.Subspace import Subspace


class SubspaceGenerationDescription(JsonSerializable, ABC):
    """"A description of how Subspaces are to be generated deterministically"""

    @abstractmethod
    def generate(self) -> list[Subspace]:
        """
        Generates the Subspaces deterministically. \n
        :return: The generated Subspaces.
        """
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, object]:
        raise NotImplementedError
