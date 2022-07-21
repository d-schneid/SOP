from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from experiments.admin.algorithm import ExperimentInline
from experiments.models.algorithm import Algorithm
from tests.unittests.views.LoggedInTestCase import AdminLoggedInTestCase


class MockRequest:
    pass


request = MockRequest()


class ExperimentInlineTests(AdminLoggedInTestCase):

    def setUp(self):
        super().setUp()
        request.user = self.admin
        self.site = AdminSite()
        self.experiment_inline = ExperimentInline(Algorithm, self.site)

    def test_experiment_inline_add_permission(self):
        algorithm = Algorithm.objects.create(signature="")
        self.assertEqual(self.experiment_inline.has_add_permission(request, algorithm), False)

    def test_experiment_inline_change_permission(self):
        self.assertEqual(self.experiment_inline.has_change_permission(request), False)

    def test_experiment_inline_delete_permission(self):
        self.assertEqual(self.experiment_inline.has_change_permission(request), False)

    def test_experiment_inline_verbose_name(self):
        self.assertEqual(self.experiment_inline.verbose_name, "Experiment")

    def test_experiment_inline_template(self):
        self.assertEqual(self.experiment_inline.template, "experiment_inline.html")


def upload_algorithm(client, name, group, description, file_name):
    path = f"tests/sample_algorithms/{file_name}"
    with open(path, "r") as file:
        data = {
            "display_name": name,
            "group": group,
            "description": description,
            "path": file,
        }
        return client.post(reverse("admin:experiments_algorithm_add"), data=data, follow=True)


class AlgorithmAdminTests(AdminLoggedInTestCase):
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

    def test_algorithm_admin_change_view(self):
        url = reverse("admin:experiments_algorithm_change", args=(self.algo.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_inline.html")
        self.assertContains(response, "Usage in experiments")
        self.assertContains(response, "Change algorithm")

    def test_admin_delete_algorithm(self):
        self.assertTrue(Algorithm.objects.exists())
        # confirm deletion on confirmation site
        data = {"post": "yes"}
        url = reverse("admin:experiments_algorithm_delete", args=(self.algo.pk,))
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{self.algo.display_name}")
        self.assertContains(response, "was deleted successfully")
        self.assertFalse(Algorithm.objects.exists())
        self.assertEqual("experiments_algorithm_changelist", response.resolver_match.url_name)

    def test_admin_add_valid_algorithm(self):
        test_name = "Test Valid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Valid Description"
        test_file_name = "SampleAlgorithmValid.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual("experiments_algorithm_changelist", response.resolver_match.url_name)
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

    def test_admin_delete_selected_algorithms_action(self):
        Algorithm.objects.create(signature="")
        self.assertTrue(Algorithm.objects.exists())
        algo_queryset = Algorithm.objects.all()
        data = {"action": "delete_selected",
                "_selected_action": [algo.pk for algo in algo_queryset],
                # confirm deletion on confirmation site
                "post": "yes"}
        url = reverse("admin:experiments_algorithm_changelist")
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Successfully deleted {algo_queryset.count()} algorithms")
        self.assertFalse(Algorithm.objects.exists())
        self.assertEqual("experiments_algorithm_changelist", response.resolver_match.url_name)