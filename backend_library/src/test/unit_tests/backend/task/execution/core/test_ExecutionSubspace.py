import unittest
from unittest.mock import Mock

import numpy as np

from backend.task.execution.core.ExecutionElement import ExecutionElement
from backend.task.execution.core.ExecutionSubspace import ExecutionSubspace
from backend.task.execution.core.Execution import Execution
from backend.task.execution.subspace.Subspace import Subspace
from backend.task.execution.ParameterizedAlgorithm import ParameterizedAlgorithm


class UnitTestExecutionSubspace(unittest.TestCase):
    # parameters for Execution
    _user_id: int = 21412
    _task_id: int = 424242

    # mock Execution
    _execution: Execution = Mock()
    _execution.user_id = Mock(return_value=_user_id)
    _execution.task_id = Mock(return_value=_task_id)

    # create Subspace
    _subspace: Subspace = Subspace(np.asarray([1, 0, 1, 1, 1]))

    # create ExecutionSubspace
    #_execution_subspace: ExecutionSubspace = ExecutionSubspace(_execution, _subspace)

    def test_getter(self):
        #self.assertEqual(self._execution_subspace.subspace, self._subspace)
        # TODO
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
