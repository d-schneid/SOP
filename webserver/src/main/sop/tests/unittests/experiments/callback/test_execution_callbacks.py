import os
from unittest import mock

import django.test

from backend.task.TaskState import TaskState
from experiments.callback.ExecutionCallbacks import execution_callback, metric_callback
from experiments.models.execution import (
    get_zip_result_path,
    ExecutionStatus,
    Execution,
    get_result_path,
)
from tests.generic import MediaMixin


def call_execution_progress_callback(execution, task_state, progress):
    objects_mock = mock.MagicMock()
    objects_mock.filter.return_value.exists.return_value = True
    objects_mock.get.return_value = execution
    with mock.patch.object(Execution, "objects", objects_mock):
        with mock.patch("os.path.exists"):
            execution_callback(execution.pk, task_state, progress)


class TestExecutionTaskProgressCallback(MediaMixin, django.test.TestCase):
    def setUp(self) -> None:
        self.execution = mock.MagicMock()
        self.execution.pk = 77
        self.execution.experiment.pk = 12
        self.execution.experiment.user.pk = 99
        self.unchanged_result_path = "not changed"
        self.changed_result_path = get_zip_result_path(self.execution)
        self.execution.result_path.name = self.unchanged_result_path
        super().setUp()

    def test_callback_finished(self):
        task_state = TaskState.FINISHED
        progress = 1.00

        call_execution_progress_callback(self.execution, task_state, progress)

        self.assertEqual(self.execution.result_path.name, self.changed_result_path)
        self.assertEqual(self.execution.status, ExecutionStatus.FINISHED.name)
        self.assertEqual(self.execution.progress, 1.00)

    def test_callback_running(self):
        task_state = TaskState.RUNNING
        progress = 0.314

        call_execution_progress_callback(self.execution, task_state, progress)

        self.assertEqual(self.execution.result_path.name, self.unchanged_result_path)
        self.assertEqual(self.execution.status, ExecutionStatus.RUNNING.name)
        self.assertEqual(self.execution.progress, 0.314)

    def test_callback_finished_with_error(self):
        task_state = TaskState.FINISHED_WITH_ERROR
        progress = 0.69

        call_execution_progress_callback(self.execution, task_state, progress)

        self.assertEqual(self.execution.result_path.name, self.changed_result_path)
        self.assertEqual(
            self.execution.status, ExecutionStatus.FINISHED_WITH_ERROR.name
        )
        self.assertEqual(self.execution.progress, 0.69)

    def test_callback_running_with_error(self):
        task_state = TaskState.RUNNING_WITH_ERROR
        progress = 0.69

        call_execution_progress_callback(self.execution, task_state, progress)

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


class TestMetricCallback(MediaMixin, django.test.TestCase):
    def setUp(self) -> None:
        self.be = mock.MagicMock()
        self.be.task_id = 3
        super().setUp()

    @mock.patch("os.path.isdir")
    @mock.patch(
        "backend.metric.MetricDataPointsAreOutliers.MetricDataPointsAreOutliers.compute_metric"
    )
    @mock.patch(
        "backend.metric.MetricSubspaceOutlierAmount.MetricSubspaceOutlierAmount.compute_metric"
    )
    def test_metric_callback(
        self, subspace_metric_mock, datapoint_metric_mock, isdir_mock
    ):
        execution = mock.MagicMock()
        execution.pk = 3
        execution.experiment.pk = 12
        execution.experiment.user.pk = 98

        objects_mock = mock.MagicMock()
        objects_mock.filter.return_value.exists.return_value = True
        objects_mock.get.return_value = execution

        # We simulate that results have been computed by creating the results directory
        os.makedirs(get_result_path(execution))

        # Attach the mocks and call the metric callback
        with mock.patch.object(Execution, "objects", objects_mock):
            with mock.patch("os.makedirs") as makedirs_mock:
                metric_callback(self.be)
                self.assertTrue(makedirs_mock.called)

        # check if both metrics are called
        self.assertTrue(subspace_metric_mock.called)
        self.assertTrue(datapoint_metric_mock.called)

    def test_metric_callback_invalid_pk(self):
        # We use an extra mock for the get method of Execution.objects to validate that
        # the callback function returned before fetching an execution if there is no
        # execution with the given task_id as its pk
        get_mock = mock.MagicMock()

        objects_mock = mock.MagicMock()
        objects_mock.filter.return_value.exists.return_value = False
        objects_mock.get = get_mock

        with mock.patch.object(Execution, "objects", objects_mock):
            metric_callback(self.be)  # type: ignore

        self.assertFalse(get_mock.called)
