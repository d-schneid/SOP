from unittest import mock

import django.test

from backend.task.TaskState import TaskState
from experiments.callback.ExecutionCallbacks import execution_callback
from experiments.models.execution import get_zip_result_path, ExecutionStatus, Execution


def call_method(execution, task_state, progress):
    objects_mock = mock.MagicMock()
    objects_mock.filter.return_value.exists.return_value = True
    objects_mock.get.return_value = execution
    with mock.patch.object(Execution, "objects", objects_mock):
        with mock.patch("os.path.exists"):
            execution_callback(execution.pk, task_state, progress)


class TestExecutionTaskProgressCallback(django.test.TestCase):
    def setUp(self) -> None:
        self.execution = mock.MagicMock()
        self.execution.pk = 77
        self.execution.experiment.pk = 12
        self.execution.experiment.user.pk = 99
        self.unchanged_result_path = "not changed"
        self.changed_result_path = get_zip_result_path(self.execution)
        self.execution.result_path.name = self.unchanged_result_path

    def test_callback_finished(self):
        task_state = TaskState.FINISHED
        progress = 1.00

        call_method(self.execution, task_state, progress)

        self.assertEqual(self.execution.result_path.name, self.changed_result_path)
        self.assertEqual(self.execution.status, ExecutionStatus.FINISHED.name)
        self.assertEqual(self.execution.progress, 1.00)

    def test_callback_running(self):
        task_state = TaskState.RUNNING
        progress = 0.314

        call_method(self.execution, task_state, progress)

        self.assertEqual(self.execution.result_path.name, self.unchanged_result_path)
        self.assertEqual(self.execution.status, ExecutionStatus.RUNNING.name)
        self.assertEqual(self.execution.progress, 0.314)

    def test_callback_finished_with_error(self):
        task_state = TaskState.FINISHED_WITH_ERROR
        progress = 0.69

        call_method(self.execution, task_state, progress)

        self.assertEqual(self.execution.result_path.name, self.changed_result_path)
        self.assertEqual(self.execution.status, ExecutionStatus.FINISHED_WITH_ERROR.name)
        self.assertEqual(self.execution.progress, 0.69)

    def test_callback_running_with_error(self):
        task_state = TaskState.RUNNING_WITH_ERROR
        progress = 0.69

        call_method(self.execution, task_state, progress)

        self.assertEqual(self.execution.result_path.name, self.unchanged_result_path)
        self.assertEqual(self.execution.status, ExecutionStatus.RUNNING_WITH_ERROR.name)
        self.assertEqual(self.execution.progress, 0.69)

    def test_callback_invalid_pk(self):
        # We should only need the objects mock since the function should exit
        # immediately if the given task_id is not matching an execution
        objects_mock = mock.MagicMock()
        objects_mock.filter.return_value.exists.return_value = False
        with mock.patch.object(Execution, "objects", objects_mock):
            execution_callback(1, TaskState.RUNNING, 0.44)

