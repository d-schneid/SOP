import os
import shutil

from django.urls import reverse

from experiments.models.dataset import Dataset, CleaningState
from sop import settings
from tests.unittests.views.generic_test_cases import AdminLoggedInTestCase


class DatasetAdminTests(AdminLoggedInTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.dataset_finished = Dataset.objects.create(
            display_name="dataset_finished_1",
            description="This is a description.",
            user=self.admin,
            status=CleaningState.FINISHED.name,
        )
        # create directory
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def tearDown(self) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def test_dataset_change_view(self):
        url = reverse("admin:experiments_dataset_change", args=(self.dataset_finished.pk,))
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dataset_finished.display_name)
        self.assertContains(response, self.dataset_finished.description)

    def test_dataset_changelist_view(self):
        url = reverse("admin:experiments_dataset_changelist")
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dataset_finished.display_name)
        self.assertContains(response, "Select dataset to change")

    def test_dataset_add_view(self):
        url = reverse("admin:experiments_dataset_add")
        response = self.client.get(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add dataset")

    def test_admin_add_dataset_valid(self):
        file_path: str = os.path.join("tests", "sample_datasets", "valid_dataset.csv")
        assert os.path.isfile(file_path)

        url = reverse("admin:experiments_dataset_add")

        with open(file_path, "r") as file:
            data = {
                "display_name": "dataset_add_valid_1",
                "description": "test",
                "user": self.admin.pk,
                "path_original": file,
                "has_header": True,
            }
            response = self.client.post(url, data, follow=True)

        assert data is not None
        assert response is not None

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "experiments_dataset_changelist")
        self.assertContains(response, "was added successfully")
        self.assertContains(response, data["display_name"])

    def test_delete_dataset(self):
        url = reverse("admin:experiments_dataset_delete", args=(self.dataset_finished.pk,))
        data = {
            "post": "yes",
        }
        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, "experiments_dataset_changelist")
        self.assertContains(response, "was deleted successfully")

    def test_delete_multiple_datasets_action(self):
        delete_datasets = [self.dataset_finished]
        data = {
            "action": "delete_selected",
            "_selected_action": [dataset.pk for dataset in delete_datasets],
            "post": "yes"  # extra prompt
        }
        url = reverse("admin:experiments_dataset_changelist")
        response = self.client.post(url, data, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertEqual("experiments_dataset_changelist", response.resolver_match.url_name)
        self.assertContains(response, "Successfully deleted")

    def test_add_dataset_invalid_file(self):
        file_path_invalid: str = os.path.join("tests", "sample_datasets", "no_csv.txt")
        assert os.path.isfile(file_path_invalid)

        url = reverse("admin:experiments_dataset_add")

        with open(file_path_invalid, "r") as file:
            data = {
                "display_name": "dataset_add_1",
                "description": "This is a description.",
                "user": self.admin.pk,
                "path_original": file,
                "has_header": True,
            }
            response = self.client.post(url, data, follow=True)

        assert data is not None
        assert response is not None

        self.assertEqual(response.status_code, 200)
        self.assertEqual("experiments_dataset_add", response.resolver_match.url_name)
        self.assertContains(response, "File extension “txt” is not allowed. Allowed extensions are: csv.")

    def test_add_dataset_invalid_user(self):
        file_path: str = os.path.join("tests", "sample_datasets", "valid_dataset.csv")
        assert os.path.isfile(file_path)

        url = reverse("admin:experiments_dataset_add")

        with open(file_path, "r") as file:
            data = {
                "display_name": "dataset_add_1",
                "description": "This is a description.",
                "user": "no_user",
                "path_original": file,
                "has_header": True,
            }
            response = self.client.post(url, data, follow=True)

        assert data is not None
        assert response is not None

        self.assertEqual(response.status_code, 200)
        self.assertEqual("experiments_dataset_add", response.resolver_match.url_name)
        self.assertContains(response, "Select a valid choice. That choice is not one of the available choices.")


