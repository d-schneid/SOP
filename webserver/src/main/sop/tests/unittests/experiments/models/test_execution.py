import math
from unittest.mock import patch, MagicMock

import django.test
from django.conf import settings
from django.db.models import Model

from experiments.models.execution import (
    generate_random_seed,
    Execution,
    get_result_path,
    get_zip_result_path,
    ExecutionStatus,
)


class ExecutionModelTests(django.test.TestCase):
    def assert_in_range(self, x: int, a: int, b: int) -> None:
        if not a <= x < b:
            raise self.failureException(f"{x} is not in range [{a}, {b})")

    def test_generate_random_seed(self) -> None:
        for _ in range(10000):
            self.assert_in_range(generate_random_seed(), 0, int(math.pow(2, 63)))

    def test_save(self) -> None:
        execution = Execution()
        self.assertIsNone(execution.subspace_generation_seed)
        with patch.object(Model, "save", lambda args: None):
            execution.save()
        self.assertIsNotNone(execution.subspace_generation_seed)

        execution = Execution()
        execution.subspace_generation_seed = 42
        self.assertIsNotNone(execution.subspace_generation_seed)
        with patch.object(Model, "save", lambda args: None):
            execution.save()
        self.assertEqual(execution.subspace_generation_seed, 42)

    def test_error_occurred(self) -> None:
        execution = Execution()
        execution.status = ExecutionStatus.RUNNING.name
        self.assertFalse(execution.error_occurred)

        execution.status = ExecutionStatus.FINISHED.name
        self.assertFalse(execution.error_occurred)

        execution.status = ExecutionStatus.FINISHED_WITH_ERROR.name
        self.assertTrue(execution.error_occurred)

    def test_is_running(self) -> None:
        execution = Execution()
        execution.status = ExecutionStatus.RUNNING.name
        self.assertTrue(execution.is_running)

        execution.status = ExecutionStatus.FINISHED.name
        self.assertFalse(execution.is_running)

        execution.status = ExecutionStatus.FINISHED_WITH_ERROR.name
        self.assertFalse(execution.is_running)

    def test_is_finished(self) -> None:
        execution = Execution()
        execution.status = ExecutionStatus.RUNNING.name
        self.assertTrue(execution.is_running)

        execution.status = ExecutionStatus.FINISHED.name
        self.assertFalse(execution.is_running)

        execution.status = ExecutionStatus.FINISHED_WITH_ERROR.name
        self.assertFalse(execution.is_running)

    def test_progress_as_percent(self) -> None:
        execution = Execution()
        execution.progress = 0.314
        self.assertEqual(execution.progress_as_percent, 31.4)

        execution.progress = 1
        self.assertEqual(execution.progress_as_percent, 100)

        execution.progress = 0
        self.assertEqual(execution.progress_as_percent, 0)

    def test_get_result_path(self) -> None:
        execution = MagicMock()
        execution.pk = 42
        execution.experiment.pk = 3
        execution.experiment.user.pk = 12
        path = get_result_path(execution)
        self.assertEqual(
            path,
            str(
                settings.MEDIA_ROOT
                / "experiments"
                / f"user_{execution.experiment.user.pk}"
                / f"experiment_{execution.experiment.pk}"
                / f"execution_{execution.pk}"
            ),
        )

    def test_get_zip_result_path(self) -> None:
        execution = MagicMock()
        execution.pk = 42
        execution.experiment.pk = 3
        execution.experiment.user.pk = 12
        path = get_zip_result_path(execution)
        self.assertEqual(
            path,
            str(
                settings.MEDIA_ROOT
                / "experiments"
                / f"user_{execution.experiment.user.pk}"
                / f"experiment_{execution.experiment.pk}"
                / f"execution_{execution.pk}.zip"
            ),
        )
