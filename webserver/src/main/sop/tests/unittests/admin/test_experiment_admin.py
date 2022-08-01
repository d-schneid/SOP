from django.urls import reverse

from tests.unittests.views.generic_test_cases import AdminLoggedInTestCase

from experiments.models.experiment import Experiment
from experiments.models.dataset import Dataset
from experiments.models.algorithm import Algorithm

from authentication.models import User


def delete_selected_experiments(client, dataset, algorithm, user):
    other_exp = Experiment.objects.create(display_name="other Exp", dataset=dataset, user=user)
    other_exp.algorithms.add(algorithm)
    exp_queryset = Experiment.objects.all()
    data = {
        "action": "delete_selected",
        "_selected_action": [exp.pk for exp in exp_queryset],
        # confirm deletion on confirmation site
        "post": "yes",
    }
    url = reverse("admin:experiments_experiment_changelist")
    return client.post(url, data, follow=True)


class AlgorithmAdminTests(AdminLoggedInTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.dataset = Dataset.objects.create(
            datapoints_total=1, dimensions_total=1, user=self.admin, is_cleaned=True
        )
        self.algo = Algorithm.objects.create(display_name="Test Algo", signature="", user=self.admin)
        self.exp = Experiment.objects.create(display_name="Test Exp", dataset=self.dataset, user=self.admin)
        self.exp.algorithms.add(self.algo)

    def test_experiment_admin_changelist_view(self):
        url = reverse("admin:experiments_experiment_changelist")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select experiment to change")
        self.assertContains(response, f"{self.exp.display_name}")

    def test_experiment_admin_change_view(self):
        url = reverse("admin:experiments_experiment_change", args=(self.exp.pk,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Change experiment")
        self.assertContains(response, f"{self.exp.display_name}")

    def test_experiment_admin_add_view(self):
        url = reverse("admin:experiments_experiment_add")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add experiment")

    def test_admin_delete_experiment(self):
        self.assertTrue(Experiment.objects.exists())
        # confirm deletion on confirmation site
        data = {"post": "yes"}
        url = reverse("admin:experiments_experiment_delete", args=(self.exp.pk,))
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{self.exp.display_name}")
        self.assertContains(response, "was deleted successfully")
        self.assertFalse(Experiment.objects.exists())
        self.assertEqual(
            "experiments_experiment_changelist", response.resolver_match.url_name
        )

    def test_admin_delete_selected_experiments_action(self):
        self.assertTrue(Experiment.objects.exists())
        response = delete_selected_experiments(self.client, self.dataset, self.algo, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Successfully deleted")
        self.assertFalse(Experiment.objects.exists())
        self.assertEqual(
            "experiments_experiment_changelist", response.resolver_match.url_name
        )

    def test_admin_change_experiment(self):
        data = {"display_name": "new display name"}
        url = reverse("admin:experiments_experiment_change", args=(self.exp.pk,))
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "changed successfully")
        self.assertContains(response, "new display name")
        self.assertEqual(
            "experiments_experiment_changelist", response.resolver_match.url_name
        )

    def test_admin_add_experiment_valid(self):
        data = {
            "display_name": "newExp",
            "user": self.admin.pk,
            "dataset": self.dataset.pk,
            "algorithms": self.algo.pk
        }
        url = reverse("admin:experiments_experiment_add")
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "was added successfully")
        self.assertContains(response, "newExp")
        self.assertEqual(
            "experiments_experiment_changelist", response.resolver_match.url_name
        )

    def test_admin_add_experiment_invalid_user(self):
        # user does not have access to self.algo and self.dataset
        user = User.objects.create(username="user", password="passwd")
        data = {
            "display_name": "newExp",
            "user": user.pk,
            "dataset": self.dataset.pk,
            "algorithms": self.algo.pk
        }
        url = reverse("admin:experiments_experiment_add")
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please correct the errors below")
        self.assertContains(response, "Selected user")
        self.assertEqual(
            "experiments_experiment_add", response.resolver_match.url_name
        )

    def test_admin_add_experiment_invalid_dataset(self):
        # dataset is not cleaned and, therefore, cannot be used
        uncleaned_dataset = Dataset.objects.create(
            datapoints_total=1, dimensions_total=1, user=self.admin, is_cleaned=False
        )
        data = {
            "display_name": "newExp",
            "user": self.admin.pk,
            "dataset": uncleaned_dataset.pk,
            "algorithms": self.algo.pk
        }
        url = reverse("admin:experiments_experiment_add")
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please correct the error below")
        self.assertContains(response, "Selected dataset is not cleaned")
        self.assertEqual(
            "experiments_experiment_add", response.resolver_match.url_name
        )