from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from tests.unittests.views.generic_test_cases import AdminLoggedInTestCase

from experiments.admin.execution import ExecutionAdmin
from experiments.models.execution import Execution, ExecutionStatus
from experiments.models.experiment import Experiment
from experiments.models.dataset import Dataset
from experiments.models.algorithm import Algorithm

from authentication.models import User


class MockRequest:
    pass


request = MockRequest()


class ExecutionAdminTests(AdminLoggedInTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = User.objects.create()
        cls.dataset = Dataset.objects.create(
            datapoints_total=1, dimensions_total=1, user=cls.user
        )
        cls.algo = Algorithm.objects.create(display_name="Test Algo", signature="",
                                             user=cls.user)
        cls.exp = Experiment.objects.create(display_name="Test Exp",
                                             dataset=cls.dataset, user=cls.user)
        cls.exp.algorithms.add(cls.algo)
        cls.exec = Execution.objects.create(experiment=cls.exp,
                                            subspace_amount=5,
                                            subspaces_max=3,
                                            subspaces_min=1,
                                            algorithm_parameters="",
                                            status=ExecutionStatus.RUNNING.name)

    def setUp(self):
        super().setUp()
        request.user = self.admin
        self.site = AdminSite()
        self.execution_admin = ExecutionAdmin(Execution, self.site)

    def test_execution_admin_add_permission(self):
        self.assertEqual(self.execution_admin.has_add_permission(request), False)

    def test_execution_admin_change_permission(self):
        self.assertEqual(self.execution_admin.has_change_permission(request), False)

    def test_execution_admin_changelist_view(self):
        url = reverse("admin:experiments_execution_changelist")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select execution to view")
        self.assertContains(response, f"{self.exec.pk}")
        self.assertContains(response, "Test Exp")

    def test_execution_admin_change_view(self):
        url = reverse("admin:experiments_execution_change", args=(self.exec.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View execution")
        self.assertContains(response, f"{self.exec.pk}")
        self.assertContains(response, "Test Exp")
        self.assertContains(response, "Delete")
        self.assertContains(response, "Close")