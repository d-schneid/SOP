from backend_library.src.main.backend.task.execution.core.Execution import Execution
from backend_library.src.main.backend.task.execution.subspace.Subspace import Subspace


class ExecutionSubspace:
    def __init__(self, execution: Execution, subspace: Subspace):
        self.execution: Execution = execution
        self.subspace: Subspace = subspace
