import os
import shutil

from django.conf import settings
from django.urls import reverse

from experiments.models import Dataset
from tests.unittests.views.generic_test_cases import LoggedInTestCase


class DatasetOverviewTests(LoggedInTestCase):
    def setUp(self) -> None:
        self.QUERYSET_NAME = "models_list"
        super().setUp()

    def create_dataset(self, name):
        return Dataset.objects.create(
            display_name=name, user=self.user, datapoints_total=0, dimensions_total=0
        )

    def test_dataset_overview_no_datasets(self):
        response = self.client.get(reverse("dataset_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_overview.html")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [])

    def test_dataset_overview_one_dataset(self):
        dataset = self.create_dataset("test_dataset")
        response = self.client.get(reverse("dataset_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_dataset")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [dataset])

    def test_dataset_overview_multiple_datasets(self):
        dataset1 = self.create_dataset("name_b")
        dataset2 = self.create_dataset("name_a")
        dataset3 = self.create_dataset("name_c")
        response = self.client.get(reverse("dataset_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_overview.html")
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(
            response.context[self.QUERYSET_NAME], [dataset2, dataset1, dataset3]
        )

    def test_dataset_overview_sort_by_upload_date(self):
        dataset1 = self.create_dataset("name_c")
        dataset2 = self.create_dataset("name_a")
        dataset3 = self.create_dataset("name_b")
        url = reverse("dataset_overview_sorted", args=("upload_date",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_overview.html")
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(
            response.context[self.QUERYSET_NAME], [dataset3, dataset2, dataset1]
        )


class DatasetUploadViewTests(LoggedInTestCase):
    def setUp(self) -> None:
        self.name = "Test Valid Dataset"
        self.description = "Test Valid Description"
        self.file_name = "valid_dataset.csv"
        super().setUp()

    @classmethod
    def setUpClass(cls):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().setUpClass()

    def tearDown(self) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def upload_dataset(self, client: str, file_name: str):
        file_path = os.path.join("tests", "sample_datasets", file_name)
        with open(file_path, "r") as file:
            data = {
                "display_name": self.name,
                "description": self.description,
                "path_original": file,
            }
            return client.post(reverse("dataset_upload"), data=data, follow=True)

    def test_dataset_upload_view_valid_upload(self):
        file_name = "valid_dataset.csv"
        response = self.upload_dataset(self.client, file_name)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, "dataset_upload.html")
        self.assertTemplateUsed(response, "dataset_overview.html")
        # we expect to be redirected to dataset_overview
        self.assertEqual("dataset_overview_sorted", response.resolver_match.url_name)
        self.assertTrue(response.redirect_chain)

        dataset = Dataset.objects.get()
        self.assertEqual(self.user, dataset.user)
        self.assertEqual(self.name, dataset.display_name)
        self.assertEqual(self.description, dataset.description)
        self.assertEqual(
            f"datasets/user_{self.user.pk}/" + self.file_name,
            str(dataset.path_original),
        )

    def test_dataset_upload_view_invalid_file_type(self):
        file_name = "invalid_dataset.txt"
        response = self.upload_dataset(self.client, file_name)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dataset_upload.html")
        self.assertTemplateNotUsed(response, "dataset_overview.html")
        # we expect to stay on the dataset_upload
        self.assertFalse(response.redirect_chain)

        dataset = Dataset.objects.first()
        self.assertIsNone(dataset)
        self.assertFalse(
            os.path.exists(f"datasets/user_{self.user.pk}/" + self.file_name)
        )


class DatasetEditViewTests(LoggedInTestCase):
    def post_dataset_edit(
        self, dataset_pk=None, expected_status=200, update_model=True
    ):
        dataset_pk = dataset_pk if dataset_pk is not None else self.dataset.pk
        data = {
            "display_name": self.new_name,
            "description": self.new_description,
        }
        response = self.client.post(
            reverse("dataset_edit", args=(dataset_pk,)), follow=True, data=data
        )
        self.assertEqual(response.status_code, expected_status)
        # reload dataset from db
        if update_model:
            self.dataset = Dataset.objects.get(pk=dataset_pk)
        return response

    def assertNoDatasetChange(self, response):
        self.assertFalse(response.redirect_chain)
        self.assertEqual(self.name, self.dataset.display_name)
        self.assertEqual(self.description, self.dataset.description)

    def assertDatasetChange(self, response):
        self.assertTrue(response.redirect_chain)
        self.assertEqual(self.new_name, self.dataset.display_name)
        self.assertEqual(self.new_description, self.dataset.description)

    def setUp(self) -> None:
        self.name = "Original Name"
        self.description = "Original Description"
        self.new_name = "New Name"
        self.new_description = "New Description"
        super().setUp()
        self.dataset = Dataset.objects.create(
            display_name=self.name,
            description=self.description,
            user=self.user,
            datapoints_total=4,
            dimensions_total=7,
        )

    def test_dataset_edit_view_valid_edit(self):
        response = self.post_dataset_edit()
        self.assertTemplateNotUsed(response, "dataset_edit.html")
        self.assertTemplateUsed(response, "dataset_overview.html")
        self.assertDatasetChange(response)

    def test_dataset_edit_view_edit_no_name(self):
        self.new_name = ""
        response = self.post_dataset_edit()
        self.assertTemplateUsed(response, "dataset_edit.html")
        self.assertTemplateNotUsed(response, "dataset_overview.html")
        self.assertNoDatasetChange(response)

    def test_dataset_edit_view_edit_no_description(self):
        self.new_description = ""
        response = self.post_dataset_edit()
        self.assertTemplateNotUsed(response, "dataset_edit.html")
        self.assertTemplateUsed(response, "dataset_overview.html")
        self.assertDatasetChange(response)

    def test_dataset_edit_view_edit_invalid_pk(self):
        response = self.post_dataset_edit(
            dataset_pk=42, expected_status=404, update_model=False
        )
        self.assertTemplateNotUsed(response, "dataset_edit.html")
        self.assertTemplateNotUsed(response, "dataset_overview.html")
        self.assertNoDatasetChange(response)


class DatasetDeleteViewTests(LoggedInTestCase):
    def test_dataset_delete_view_valid_delete(self):
        dataset = Dataset.objects.create(
            datapoints_total=0, dimensions_total=0, user=self.user
        )
        response = self.client.post(
            reverse("dataset_delete", args=(dataset.pk,)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertIsNone(Dataset.objects.first())
        self.assertTemplateUsed(response, "dataset_overview.html")

    def test_dataset_delete_view_invalid_pk(self):
        response = self.client.post(reverse("dataset_delete", args=(42,)), follow=True)
        # we expect to be redirected to the dataset overview
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, "dataset_overview.html")
