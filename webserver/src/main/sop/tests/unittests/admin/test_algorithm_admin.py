import django.test
from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from experiments.admin.inlines import ExperimentInlineAlgorithm
from experiments.models.algorithm import Algorithm
from experiments.models.dataset import Dataset
from experiments.models.experiment import Experiment
from tests.generic import AdminLoggedInMixin


class MockRequest:
    pass


request = MockRequest()


class ExperimentInlineTests(AdminLoggedInMixin, django.test.TestCase):
    def setUp(self):
        super().setUp()
        request.user = self.admin
        self.site = AdminSite()
        self.experiment_inline = ExperimentInlineAlgorithm(Algorithm, self.site)

    def test_experiment_inline_add_permission(self):
        algorithm = Algorithm.objects.create(signature="")
        self.assertFalse(self.experiment_inline.has_add_permission(request, algorithm))

    def test_experiment_inline_change_permission(self):
        self.assertFalse(self.experiment_inline.has_change_permission(request))

    def test_experiment_inline_delete_permission(self):
        self.assertFalse(self.experiment_inline.has_change_permission(request))

    def test_experiment_inline_template(self):
        self.assertEqual(
            self.experiment_inline.template,
            "admin/experiment/experiment_inline_algorithm.html",
        )


def upload_algorithm(client, name, group, description, file_name):
    path = f"tests/sample_algorithms/{file_name}"
    with open(path, "r") as file:
        data = {
            "display_name": name,
            "group": group,
            "description": description,
            "path": file,
        }
        return client.post(
            reverse("admin:experiments_algorithm_add"), data=data, follow=True
        )


def delete_selected_algorithms(client):
    Algorithm.objects.create(signature="")
    algo_queryset = Algorithm.objects.all()
    data = {
        "action": "delete_selected",
        "_selected_action": [algo.pk for algo in algo_queryset],
        # confirm deletion on confirmation site
        "post": "yes",
    }
    url = reverse("admin:experiments_algorithm_changelist")
    return client.post(url, data, follow=True)


class AlgorithmAdminTests(AdminLoggedInMixin, django.test.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.algo = Algorithm.objects.create(display_name="Test Algo", signature="")

    def test_algorithm_admin_changelist_view(self):
        url = reverse("admin:experiments_algorithm_changelist")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select algorithm to change")
        self.assertContains(response, f"{self.algo.display_name}")

    def test_algorithm_admin_add_view(self):
        url = reverse("admin:experiments_algorithm_add")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add algorithm")

    def test_algorithm_admin_change_view_inline(self):
        dataset = Dataset.objects.create(
            datapoints_total=1, dimensions_total=1, user=self.admin
        )
        exp = Experiment.objects.create(
            display_name="exp", dataset=dataset, user=self.admin
        )
        # Experiment shall be shown in inline
        exp.algorithms.add(self.algo)
        url = reverse("admin:experiments_algorithm_change", args=(self.algo.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Change algorithm")
        self.assertTemplateUsed(
            response, "admin/experiment/experiment_inline_algorithm.html"
        )
        self.assertContains(response, "Usage in experiments")
        self.assertContains(response, f"{exp.display_name}")

    def test_algorithm_admin_change_view_no_inline(self):
        url = reverse("admin:experiments_algorithm_change", args=(self.algo.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Change algorithm")
        self.assertTemplateUsed(
            response, "admin/experiment/experiment_inline_algorithm.html"
        )
        self.assertContains(response, "Usage in experiments")
        self.assertContains(response, "Not used in any experiment")

    def test_admin_delete_algorithm_valid(self):
        self.assertTrue(Algorithm.objects.exists())
        # confirm deletion on confirmation site
        data = {"post": "yes"}
        url = reverse("admin:experiments_algorithm_delete", args=(self.algo.pk,))
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{self.algo.display_name}")
        self.assertContains(response, "was deleted successfully")
        self.assertFalse(Algorithm.objects.exists())
        self.assertEqual(
            "experiments_algorithm_changelist", response.resolver_match.url_name
        )

    def test_admin_delete_algorithm_invalid(self):
        self.dataset = Dataset.objects.create(
            datapoints_total=1, dimensions_total=1, user=self.admin
        )
        self.exp = Experiment.objects.create(
            display_name="Test Exp", dataset=self.dataset, user=self.admin
        )
        self.exp.algorithms.add(self.algo)
        self.assertTrue(Algorithm.objects.exists())
        # confirm deletion on confirmation site
        data = {"post": "yes"}
        url = reverse("admin:experiments_algorithm_delete", args=(self.algo.pk,))
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{self.algo.display_name}")
        self.assertContains(response, "cannot be deleted")
        self.assertContains(response, "is used in at least one experiment")
        self.assertTrue(Algorithm.objects.exists())
        self.assertEqual(
            "experiments_algorithm_delete", response.resolver_match.url_name
        )

    def test_admin_add_valid_algorithm(self):
        test_name = "Test Valid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Valid Description"
        test_file_name = "SampleAlgorithmValid.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            "experiments_algorithm_changelist", response.resolver_match.url_name
        )
        self.assertContains(response, "Select algorithm to change")

    def test_admin_add_invalid_algorithm(self):
        test_name = "Test Valid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Valid Description"
        test_file_name = "SampleAlgorithmInvalid.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual("experiments_algorithm_add", response.resolver_match.url_name)
        self.assertContains(response, "This is not a valid algorithm")

    def test_admin_delete_selected_algorithms_action_valid(self):
        self.assertTrue(Algorithm.objects.exists())
        response = delete_selected_algorithms(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Successfully deleted")
        self.assertFalse(Algorithm.objects.exists())
        self.assertEqual(
            "experiments_algorithm_changelist", response.resolver_match.url_name
        )

    def test_admin_delete_selected_algorithms_action_invalid(self):
        dataset = Dataset.objects.create(
            datapoints_total=1, dimensions_total=1, user=self.admin
        )
        exp = Experiment.objects.create(dataset=dataset, user=self.admin)
        # Algorithm is used in experiemnt, therefore no bulk deletion possible
        exp.algorithms.add(self.algo)
        response = delete_selected_algorithms(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bulk deletion cannot be executed")
        self.assertTrue(Algorithm.objects.exists())
        self.assertEqual(
            "experiments_algorithm_changelist", response.resolver_match.url_name
        )
