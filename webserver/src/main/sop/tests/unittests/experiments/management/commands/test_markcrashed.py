import django.test

from authentication.models import User
from experiments.models import Execution, Dataset, Experiment
from experiments.models.execution import ExecutionStatus
from experiments.management.commands.markcrashed import Command


class MarkCrashedTests(django.test.TestCase):
    user1: User
    dataset1: Dataset
    exp1: Experiment
    exe1: Execution
    exe2: Execution
    exe3: Execution
    exe4: Execution
    exe5: Execution

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user1 = User.objects.create(username="1", password="pswd")
        cls.dataset1 = Dataset.objects.create(user=cls.user1, display_name="D1")
        cls.exp1 = Experiment.objects.create(
            user=cls.user1, display_name="A", dataset=cls.dataset1
        )
        cls.exe1 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=2,
            subspaces_min=1,
            subspaces_max=3,
            status=ExecutionStatus.RUNNING.name,
        )
        cls.exe2 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
            status=ExecutionStatus.RUNNING_WITH_ERROR.name,
        )
        cls.exe3 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
            status=ExecutionStatus.CRASHED.name,
        )
        cls.exe4 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
            status=ExecutionStatus.FINISHED.name,
        )
        cls.exe5 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
            status=ExecutionStatus.FINISHED_WITH_ERROR.name,
        )

    def test_mark_crashed(self) -> None:
        cmd = Command()
        cmd.handle()
        self.exe1.refresh_from_db()
        self.assertEqual(ExecutionStatus.CRASHED.name, self.exe1.status)
        self.exe2.refresh_from_db()
        self.assertEqual(ExecutionStatus.CRASHED.name, self.exe2.status)
        self.exe3.refresh_from_db()
        self.assertEqual(ExecutionStatus.CRASHED.name, self.exe3.status)
        self.exe4.refresh_from_db()
        self.assertEqual(ExecutionStatus.FINISHED.name, self.exe4.status)
        self.exe5.refresh_from_db()
        self.assertEqual(ExecutionStatus.FINISHED_WITH_ERROR.name, self.exe5.status)
