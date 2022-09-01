import django.test

from authentication.models import User
from experiments.models import Execution, Dataset, Experiment
from experiments.models.execution import ExecutionStatus
from experiments.management.commands.markcrashed import Command


class PyodToDBTests(django.test.TestCase):
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
            status=ExecutionStatus.FINISHED.name,
        )
        cls.exe4 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
            status=ExecutionStatus.FINISHED_WITH_ERROR.name,
        )
        cls.exe5 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
            status=ExecutionStatus.CRASHED.name,
        )

    def test_mark_crashed(self) -> None:
        cmd = Command()
        cmd.handle()
        for execution in Execution.objects.get_queryset():
            if execution.pk in [1, 2, 5]:
                self.assertEqual(ExecutionStatus.CRASHED.name, execution.status)
            elif execution.pk == 3:
                self.assertEqual(ExecutionStatus.FINISHED.name, execution.status)
            elif execution.pk == 4:
                self.assertEqual(ExecutionStatus.FINISHED_WITH_ERROR.name, execution.status)
