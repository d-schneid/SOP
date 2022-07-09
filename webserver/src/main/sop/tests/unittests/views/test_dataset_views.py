import os
import shutil

from django.urls import reverse

from experiments.models import Dataset
from django.conf import settings

from tests.unittests.views.LoggedInTestCase import LoggedInTestCase


class DatasetOverviewTests(LoggedInTestCase):

    def setUp(self) -> None:
        self.QUERYSET_NAME = "models_list"
        super().setUp()

    def create_dataset(self, name):
        return Dataset.objects.create(name=name, user=self.user, datapoints_total=0, dimensions_total=0)

    def test_no_datasets(self):
        response = self.client.get(reverse("dataset_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [])

    def test_one_dataset(self):
        dataset = self.create_dataset("test_dataset")
        response = self.client.get(reverse("dataset_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_dataset")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [dataset])

    def test_multiple_datasets(self):
        dataset1 = self.create_dataset("name_b")
        dataset2 = self.create_dataset("name_a")
        dataset3 = self.create_dataset("name_c")
        response = self.client.get(reverse("dataset_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [dataset2, dataset1, dataset3])

    def test_sort_by_upload_date(self):
        dataset1 = self.create_dataset("name_c")
        dataset2 = self.create_dataset("name_a")
        dataset3 = self.create_dataset("name_b")
        url = reverse("dataset_overview_sorted", args=("upload_date",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [dataset3, dataset2, dataset1])





class DatasetUploadViewTests(LoggedInTestCase):

    def setUp(self) -> None:
        self.name = "Test Valid Dataset"
        self.description = "Test Valid Description"
        self.file_name = "valid_dataset.csv"
        self.subspaces_min = 1
        self.subspaces_max = 4
        self.subspace_amount = 2
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

    def upload_dataset(self, client, file_name):
        path = f"tests/sample_datasets/{file_name}"
        with open(path, "r") as file:
            data = {
                "name": self.name,
                "description": self.description,
                "path_original": file,
            }
            return client.post(reverse("dataset_upload"), data=data, follow=True)

    def test_valid_upload(self):
        file_name = "valid_dataset.csv"
        response = self.upload_dataset(self.client, file_name)

        self.assertEqual(response.status_code, 200)
        # we expect to be redirected to algorithm_overview
        self.assertEqual("dataset_overview_sorted", response.resolver_match.url_name)
        self.assertTrue(response.redirect_chain)

        dataset = Dataset.objects.get()
        self.assertEqual(self.name, dataset.name)
        self.assertEqual(self.description, dataset.description)
        self.assertEqual(f"datasets/user_{self.user.pk}/" + self.file_name, str(dataset.path_original))

    def test_invalid_file_type(self):
        file_name = "invalid_dataset.txt"
        response = self.upload_dataset(self.client, file_name)

        self.assertEqual(response.status_code, 200)
        # we expect to be redirected to algorithm_overview
        self.assertFalse(response.redirect_chain)

        dataset = Dataset.objects.first()
        self.assertIsNone(dataset)
        self.assertFalse(os.path.exists(f"datasets/user_{self.user.pk}/" + self.file_name))
