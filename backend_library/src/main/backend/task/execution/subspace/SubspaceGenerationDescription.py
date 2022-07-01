import string
from collections.abc import Iterable
from abc import ABC, abstractmethod

from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace


class SubspaceGenerationDescription(ABC):
    # returns a Subspace[]
    @abstractmethod
    def generate(self) -> Iterable[Subspace]:
        return iter([])

    # Create a dictionary first with all values that should be visualized and convert it into the json
    @abstractmethod
    def to_json(self) -> string:
        return ""
