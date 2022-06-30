import string
from collections.abc import Iterable
from abc import ABC, abstractmethod

from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace


class SubspaceGenerationDescription(ABC):
    @abstractmethod
    def parameters_are_correct(self) -> bool:
        return True

    # returns a Subspace[]
    @abstractmethod
    def generate(self) -> Iterable[Subspace]:
        return Subspace[0]

    @abstractmethod
    def to_json(self) -> string:
        # Create a dictionary first with all values that should be visualized and convert it into the json
        return ""
