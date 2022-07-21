from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from experiments.admin.algorithm import ExperimentInline
from experiments.models.algorithm import Algorithm
from tests.unittests.views.LoggedInTestCase import AdminLoggedInTestCase


class ExperimentInlineTests(AdminLoggedInTestCase):
    class MockRequest:
        pass

    def setUp(self):
        super().setUp()
        self.request = self.MockRequest()
        self.request.user = self.admin
        self.site = AdminSite()
        self.experiment_inline = ExperimentInline(Algorithm, self.site)

    def test_experiment_inline_add_permission(self):
        algorithm = Algorithm.objects.create(signature="")
        self.assertEqual(self.experiment_inline.has_add_permission(self.request, algorithm), False)

    def test_experiment_inline_change_permission(self):
        self.assertEqual(self.experiment_inline.has_change_permission(self.request), False)

    def test_experiment_inline_delete_permission(self):
        self.assertEqual(self.experiment_inline.has_change_permission(self.request), False)

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
    @classmethod
    def setUpTestData(cls):
        cls.algorithm = Algorithm.objects.create(
            signature="",
        )

    def test_algorithm_admin_changelist_view(self):
        url = reverse("admin:experiments_algorithm_changelist")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_algorithm_admin_add_view(self):
        url = reverse("admin:experiments_algorithm_add")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_algorithm_admin_change_view(self):
        url = reverse("admin:experiments_algorithm_change", args=(self.algorithm.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_inline.html")
        self.assertContains(response, "Usage in experiments")

    def test_admin_add_valid_algorithm(self):
        test_name = "Test Valid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Valid Description"
        test_file_name = "SampleAlgorithmValid.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "experiments_algorithm_changelist")

    def test_admin_add_invalid_algorithm(self):
        test_name = "Test Valid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Valid Description"
        test_file_name = "SampleAlgorithmInvalid.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "experiments_algorithm_add")
        self.assertContains(response, "This is not a valid algorithm")
