from typing import Any
from unittest.mock import patch, MagicMock

import django.test
from django.http import HttpResponse
from django.urls import reverse_lazy

from experiments.models import Experiment, Dataset, Algorithm, Execution
from tests.generic import LoggedInMixin, MediaMixin, DebugSchedulerMixin


class ExecutionCreateViewTests(
    LoggedInMixin, DebugSchedulerMixin, MediaMixin, django.test.TestCase
):
    dataset: Dataset
    algo1: Algorithm
    algo2: Algorithm
    exp: Experiment
    data: dict[str, Any]

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

    def send_post(self, schedule_error=False) -> HttpResponse:
        schedule_backend_mock = MagicMock()
        if schedule_error:
            schedule_backend_mock.return_value = {
                "test_error": ["This is a test error message"]
            }
        else:
            schedule_backend_mock.return_value = None

        with patch(
            "experiments.views.execution.schedule_backend", schedule_backend_mock
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

    def test_execution_create_view_subspace_errors2(self) -> None:
        """
        Test that Subspaces max is greater than or equal to Subspaces min.
        """
        self.data["subspaces_min"] = 0
        self.data["subspaces_max"] = 2
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertEqual(
            str(response.context["form"]).find("greater than or equal to 0"), -1
        )
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspace_errors3(self) -> None:
        self.data["subspaces_min"] = self.dataset.dimensions_total
        self.data["subspaces_max"] = self.dataset.dimensions_total
        self.data["subspace_amount"] = 2
        # In this test, schedule_backend will return an error
        response = self.send_post(schedule_error=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspace_errors4(self) -> None:
        self.data["subspaces_max"] = self.dataset.dimensions_total + 1
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspace_errors5(self) -> None:
        self.data["subspace_amount"] = 0
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertIsNone(Execution.objects.first())

    def test_execution_create_view_subspace_errors6(self) -> None:
        self.data["subspaces_min"] = -4
        self.data["subspaces_max"] = -4
        self.data["subspace_amount"] = -4
        response = self.send_post()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)
        self.assertIsNone(Execution.objects.first())


class ExecutionDuplicateViewTests(LoggedInMixin, django.test.TestCase):
    dataset: Dataset
    algo1: Algorithm
    algo2: Algorithm
    exp: Experiment
    data: dict[str, Any]
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

    def test_execution_duplicate_view_get(self) -> None:
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
