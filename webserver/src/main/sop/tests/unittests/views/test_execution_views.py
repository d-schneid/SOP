from typing import Any, Dict
from unittest.mock import patch, MagicMock

import django.test
from django.http import HttpResponse
from django.urls import reverse_lazy

from backend.task.execution.core.Execution import Execution as BackendExecution
from experiments.models import Experiment, Dataset, Algorithm, Execution
from experiments.views.execution import schedule_backend
from tests.generic import LoggedInMixin, MediaMixin, DebugSchedulerMixin


class ExecutionCreateViewTests(
    LoggedInMixin, DebugSchedulerMixin, MediaMixin, django.test.TestCase
):
    dataset: Dataset
    algo1: Algorithm
    algo2: Algorithm
    exp: Experiment
    data: Dict[str, Any]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.dataset = Dataset.objects.create(user=cls.user, dimensions_total=10)
        cls.exp = Experiment.objects.create(dataset=cls.dataset, user=cls.user)
        cls.algo1 = Algorithm.objects.create(
            display_name="Algo 1",
            signature={"param1": 5, "param2": "Hello"},
        )
        cls.algo2 = Algorithm.objects.create(
            display_name="Algo 2", signature={"param1": 4.8, "param2": None}
        )
        cls.exp.algorithms.set([cls.algo1, cls.algo2])  # noqa
        cls.data = {
            "subspaces_min": 3,
            "subspaces_max": 6,
            "subspace_amount": 4,
            "subspace_generation_seed": 42,
            f"{cls.algo1.pk}_param1": "8",
            f"{cls.algo1.pk}_param2": "'World'",
            f"{cls.algo2.pk}_param1": "3.14",
            f"{cls.algo2.pk}_param2": "'was None'",
        }

    def send_post(self) -> HttpResponse:
        with patch(
            "experiments.views.execution.schedule_backend", lambda execution: None
        ):
            response = self.client.post(
                reverse_lazy("execution_create", args=(self.exp.pk,)),
                data=self.data,
                follow=True,
            )
            return response  # type: ignore

    def test_execution_create_view(self) -> None:
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed("experiment_overview")
        execution = Execution.objects.first()
        self.assertIsNotNone(execution)

    def test_execution_create_view_with_errors(self) -> None:
        self.data[f"{self.algo1.pk}_param1"] = "{'key': 'value"
        self.data[f"{self.algo1.pk}_param2"] = "variable"
        self.data[f"{self.algo2.pk}_param1"] = "'String"
        self.data[f"{self.algo2.pk}_param2"] = "3.8.5"
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertContains(response, f"{self.algo1.display_name}.param1")
        self.assertContains(response, f"{self.algo1.display_name}.param2")
        self.assertContains(response, f"{self.algo2.display_name}.param1")
        self.assertContains(response, f"{self.algo2.display_name}.param2")
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspace_errors(self) -> None:
        self.data["subspaces_min"] = -3
        self.data["subspaces_max"] = 200
        self.data["subspace_amount"] = -34
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertNotEqual(
            str(response.context["form"]).find("greater than or equal to 0"), -1
        )
        # self.assertContains(response, "Value must be greater than or equal to 0")
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspcace_max_greater_than_dimensions(self) -> None:
        self.data["subspaces_max"] = self.dataset.dimensions_total + 1
        response = self.send_post()

        self.assertEqual(response.status_code, 200)
        # Execution was not created
        self.assertIsNone(Execution.objects.first())
        self.assertFalse(response.redirect_chain)

        self.assertEqual(len(response.context["messages"]), 1)

    def test_execution_create_view_subspace_errors2(self) -> None:
        """
        Test that Subspaces max is greater than or equal to Subspaces min.
        """
        self.data["subspaces_min"] = 4
        self.data["subspaces_max"] = 2
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        messages = list(response.context["messages"])
        self.assertEqual(
            str(response.context["form"]).find("greater than or equal to 0"), -1
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            len([m for m in messages if "Min" in m.message and "Max" in m.message]), 1
        )
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspace_errors3(self) -> None:
        """
        Test that subspace generation seed and Subspace amount cannot be smaller than zero
        """
        self.data["subspace_generation_seed"] = -1
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertNotEqual(
            str(response.context["form"]).find("greater than or equal to 0"), -1
        )
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspace_errors4(self) -> None:
        """
        Test that subspace min and max can't be smaller than 0, even if min < max.
        """
        self.data["subspaces_min"] = -2
        self.data["subspaces_max"] = -1
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertNotEqual(
            str(response.context["form"]).find("greater than or equal to 0"), -1
        )
        self.assertIsNone(Execution.objects.first())

    def test_schedule_backend(self) -> None:
        algo1 = MagicMock()
        algo1.path.path = "algorithm/path"
        algo1.display_name = "Algo 1"
        algo1.pk = 69
        algo2 = MagicMock()
        algo2.path.path = "algorithm/path/2"
        algo2.display_name = "Algo 2"
        algo2.pk = 42
        execution = MagicMock()
        execution.pk = 12
        execution.subspaces_min = 2
        execution.subspaces_max = 5
        execution.subspace_amount = 3
        execution.subspace_generation_seed = 123456789
        execution.get_result_path.return_value = "another/cool/path"
        execution.algorithm_parameters = {
            f"{algo1.pk}": {"param1": 8, "param2": "World"},
            f"{algo2.pk}": {"param1": 3.14, "param2": "was None"},
        }

        execution.experiment.dataset.dimensions_total = 20
        execution.experiment.dataset.path_cleaned.path = (
            "cool/path/to/dataset_cleaned.csv"
        )
        execution.experiment.dataset.datapoints_total = 200

        execution.experiment.user.pk = 3
        execution.experiment.algorithms.all.return_value = [algo1, algo2]

        with patch.object(BackendExecution, "schedule", lambda s: None):
            errors = schedule_backend(execution)
            self.assertIsNone(errors)

    def test_schedule_backend_not_enough_subspaces(self) -> None:
        execution = MagicMock()
        execution.pk = 12
        execution.subspaces_min = 2
        execution.subspaces_max = 5
        execution.subspace_amount = 1000

        execution.experiment.dataset.dimensions_total = 20
        execution.experiment.algorithms.all.return_value = []

        with patch.object(BackendExecution, "schedule", lambda s: None):
            errors = schedule_backend(execution)
            assert errors is not None
            self.assertEqual(len(errors.keys()), 1)
            self.assertIsNotNone(errors.get("subspace_amount"))


class ExecutionDuplicateViewTests(LoggedInMixin, django.test.TestCase):
    dataset: Dataset
    algo1: Algorithm
    algo2: Algorithm
    exp: Experiment
    data: Dict[str, Any]
    execution: Execution

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.dataset = Dataset.objects.create(user=cls.user, dimensions_total=10000)
        cls.exp = Experiment.objects.create(dataset=cls.dataset, user=cls.user)
        cls.algo1 = Algorithm.objects.create(
            display_name="Algo 1",
            signature={"param1": 5, "param2": "Hello"},
        )
        cls.algo2 = Algorithm.objects.create(
            display_name="Algo 2", signature={"param1": 4.8, "param2": None}
        )
        cls.exp.algorithms.set([cls.algo1, cls.algo2])  # noqa
        cls.execution = Execution.objects.create(
            experiment=cls.exp,
            subspace_amount=42,
            subspaces_min=69,
            subspaces_max=99,
            algorithm_parameters={
                f"{cls.algo1.pk}": {"param1": 12, "param2": "World"},
                f"{cls.algo2.pk}": {"param1": 3.14, "param2": "was None"},
            },
        )

    def test_experiment_duplicate_view_get(self) -> None:
        response = self.client.get(
            reverse_lazy(
                "execution_duplicate",
                args=(self.execution.experiment.pk, self.execution.pk),
            )
        )
        self.assertContains(response, "42")
        self.assertContains(response, "69")
        self.assertContains(response, "99")
        self.assertContains(response, "12")
        self.assertContains(response, "&quot;World&quot;")
        self.assertContains(response, "3.14")
        self.assertContains(response, "&quot;was None&quot;")
