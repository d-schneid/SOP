from abc import ABC, abstractmethod
from typing import List, Dict

from backend.task.execution.subspace.Subspace import Subspace


class SubspaceGenerationDescription(ABC):
    """"A description of how Subspaces are to be generated deterministically"""
    @abstractmethod
    def generate(self) -> List[Subspace]:
        """
        Generates the Subspaces deterministically. \n
        :return: The generated Subspaces.
        """
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> Dict[str, object]:
        """
        Converts the important information of the SubspaceGenerationDescription into a JSON-string, so that the
        Subspace generation can be understood and reproduced. \n
        :return: the JSON-string
        """
        pass
