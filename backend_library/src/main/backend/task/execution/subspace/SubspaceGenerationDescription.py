import string
from collections.abc import Iterable

from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace


class SubspaceGenerationDescription:
    def parameters_are_correct(self) -> bool:
        return True

    # returns a Subspace[]
    def generate(self) -> Iterable[Subspace]:
        return Subspace[0]

    def to_json(self) -> string:
        # Create a dictionary first with all values that should be visualized and convert it into the json
        return ""
