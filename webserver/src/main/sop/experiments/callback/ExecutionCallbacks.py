import os
from pathlib import Path

from django.utils import timezone

from backend.metric.MetricDataPointsAreOutliers import MetricDataPointsAreOutliers
from backend.metric.MetricSubspaceOutlierAmount import MetricSubspaceOutlierAmount
from backend.task import TaskState
from backend.task.execution.core.Execution import Execution as BackendExecution
from experiments.models import Execution
from experiments.models.execution import (
    get_zip_result_path,
    ExecutionStatus,
    get_result_path,
)


def execution_callback(
    task_id: int, task_state: TaskState.TaskState, progress: float
) -> None:
    """
    The progress callback function used by the backend execution task. It will update
    the progress and state of an execution model based on the progress and state of the
    backend task.
    @param task_id: the task id of the backend task which will be the executions primary
    key
    @param task_state: The TaskState of the backend execution.
    @param progress: The progress of the backend execution.
    @return: None
    """
    print("execution callback", task_id, task_state, progress)
    execution: Execution = Execution.objects.get(pk=task_id)

    if task_state.is_finished():
        zip_path = get_zip_result_path(execution)
        assert os.path.exists(zip_path)
        execution.result_path.name = get_zip_result_path(execution)
        execution.finished_date = timezone.now()

    if task_state.is_finished() and not task_state.error_occurred():
        execution.status = ExecutionStatus.FINISHED.name
    elif task_state.is_finished() and task_state.error_occurred():
        execution.status = ExecutionStatus.FINISHED_WITH_ERROR.name
    elif task_state.is_running() and not task_state.error_occurred():
        execution.status = ExecutionStatus.RUNNING.name
    elif task_state.is_running() and task_state.error_occurred():
        execution.status = ExecutionStatus.RUNNING_WITH_ERROR.name

    execution.progress = progress

    execution.save()

    # TODO debug
    test_exec_all = Execution.objects.all()
    print("--DEBUG execution callback----")
    print(test_exec_all)
    test_exec = test_exec_all.first()
    print(test_exec)
    print(test_exec.status)
    print(test_exec.progress)
    print("--DEBUG execution callback END---")


def generate_datapoints_metric(metric_dir: Path, be: BackendExecution):
    assert os.path.isdir(metric_dir)
    metric_result_path = metric_dir / "datapoints_metric.csv"
    metric = MetricDataPointsAreOutliers(indices_mapping=be.dataset_indices)
    metric.compute_metric(
        metric_result_path=str(metric_result_path),
        algorithm_directory_paths=be.algorithm_directory_paths,
    )


def generate_subspace_outlier_metric(metric_dir: Path, be: BackendExecution):
    assert os.path.exists(metric_dir)
    metric_result_path = metric_dir / "subspace_outliers.csv"
    metric = MetricSubspaceOutlierAmount()
    metric.compute_metric(
        metric_result_path=str(metric_result_path),
        algorithm_directory_paths=be.algorithm_directory_paths,
    )


def metric_callback(be: BackendExecution) -> None:
    """
    The metric callback used by the backend execution task. It calls metrics in the
    backend and saves their results in the executions results path before it is zipped.
    @param be: The backend execution object on which the metrics will be called.
    @return: None
    """
    print(f"metric callback for execution {be.task_id}")
    execution_pk = be.task_id
    if not Execution.objects.filter(pk=execution_pk).exists():
        return

    execution = Execution.objects.get(pk=execution_pk)
    metric_dir = Path(get_result_path(execution)) / "metrics"
    assert os.path.isdir(metric_dir.parent)
    os.makedirs(metric_dir)

    generate_datapoints_metric(metric_dir, be)
    generate_subspace_outlier_metric(metric_dir, be)
