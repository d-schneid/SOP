from unittest.mock import MagicMock, patch

import django.test
from django.contrib.admin.sites import AdminSite
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from authentication.models import User
from experiments.admin.execution import ExecutionAdmin
from experiments.models.algorithm import Algorithm
from experiments.models.dataset import Dataset
from experiments.models.execution import Execution, ExecutionStatus
from experiments.models.experiment import Experiment
from experiments.views.execution import download_execution_result_admin
from tests.generic import AdminLoggedInMixin


class MockRequest:
    pass


request = MockRequest()


class ExecutionAdminTests(AdminLoggedInMixin, django.test.TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = User.objects.create()
        cls.dataset = Dataset.objects.create(
            datapoints_total=1, dimensions_total=1, user=cls.user
        )
        cls.algo = Algorithm.objects.create(
            display_name="Test Algo", signature="", user=cls.user
        )
        cls.exp = Experiment.objects.create(
            display_name="Test Exp", dataset=cls.dataset, user=cls.user
        )
        cls.exp.algorithms.add(cls.algo)
        cls.exec = Execution.objects.create(
            experiment=cls.exp,
            subspace_amount=5,
            subspaces_max=3,
            subspaces_min=1,
            algorithm_parameters="",
            status=ExecutionStatus.RUNNING.name,
        )

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

    def test_execution_admin_change_view_no_result(self):
        url = reverse("admin:experiments_execution_change", args=(self.exec.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View execution")
        self.assertContains(response, f"{self.exec.pk}")
        self.assertContains(response, "Test Exp")
        self.assertContains(response, "Delete")
        self.assertContains(response, "Close")

    def test_execution_admin_change_view_result(self):
        exec_with_result = Execution.objects.create(
            experiment=self.exp,
            subspace_amount=5,
            subspaces_max=3,
            subspaces_min=1,
            algorithm_parameters="",
            status=ExecutionStatus.FINISHED.name,
        )
        url = reverse("admin:experiments_execution_change", args=(exec_with_result.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View execution")
        self.assertContains(response, f"{self.exec.pk}")
        self.assertContains(response, "Test Exp")
        self.assertContains(response, "Delete")
        self.assertContains(response, "Close")
        self.assertContains(response, "Result")
        self.assertContains(response, "Download")

    def test_download_execution_result_admin(self) -> None:
        content = "Line 1\nLine 2\nLast Line"
        new_request = MagicMock()
        new_request.method = "GET"
        objects_mock = MagicMock()
        objects_mock.filter.return_value.first.return_value.result_path.__enter__.return_value.read.return_value = (
            content
        )
        with patch.object(Execution, "objects", objects_mock):
            response = download_execution_result_admin(new_request, 1)
            self.assertIsNotNone(response)
            assert isinstance(response, HttpResponse)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, bytes(content, "utf-8"))
            self.assertEqual(
                response["Content-Disposition"], "attachment; filename=result.zip"
            )

    def test_download_execution_result_admin_invalid_pk(self) -> None:
        new_request = MagicMock()
        new_request.method = "GET"
        objects_mock = MagicMock()
        objects_mock.filter.return_value.first.return_value = None
        with patch.object(Execution, "objects", objects_mock):
            response = download_execution_result_admin(new_request, 1)
            self.assertIsNotNone(response)
            assert isinstance(response, HttpResponseRedirect)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url, reverse_lazy("admin:experiments_execution_changelist")
            )

    def test_download_execution_result_admin_post(self) -> None:
        content = "Line 1\nLine 2\nLast Line"
        new_request = MagicMock()
        new_request.method = "POST"
        objects_mock = MagicMock()
        objects_mock.filter.return_value.first.return_value.result_path.__enter__.return_value.read.return_value = (
            content
        )
        with patch.object(Execution, "objects", objects_mock):
            response = download_execution_result_admin(new_request, 1)
            self.assertIsNone(response)
