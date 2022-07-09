import os
import shutil
from unittest import skip

from django.test import TestCase
from django.urls import reverse

from authentication.models import User
from experiments.models import Algorithm
from django.conf import settings


class AlgorithmOverviewTests(TestCase):

    def setUp(self) -> None:
        self.QUERYSET_NAME = "models_list"
        self.credentials = {
            "username": "user",
            "password": "passwd"
        }
        User.objects.create_user(**self.credentials)
        self.client.post(reverse("login"), self.credentials, follow=True)

    def test_no_algorithms(self):
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [])

    def test_one_algorithm(self):
        algorithm = Algorithm.objects.create(name="test_algo")
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_algo")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algorithm])

    def test_multiple_algorithms(self):
        algo1 = Algorithm.objects.create(name="name_b")
        algo2 = Algorithm.objects.create(name="name_a")
        algo3 = Algorithm.objects.create(name="name_c")
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo2, algo1, algo3])

    def test_sort_by_group(self):
        algo1 = Algorithm.objects.create(group=Algorithm.AlgorithmGroup.PROBABILISTIC)
        algo2 = Algorithm.objects.create(group=Algorithm.AlgorithmGroup.COMBINATION)
        algo3 = Algorithm.objects.create(group=Algorithm.AlgorithmGroup.LINEAR_MODEL)
        url = reverse("algorithm_overview_sorted", args=("group",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Algorithm.AlgorithmGroup.PROBABILISTIC)
        self.assertContains(response, Algorithm.AlgorithmGroup.COMBINATION)
        self.assertContains(response, Algorithm.AlgorithmGroup.LINEAR_MODEL)
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo2, algo3, algo1])

    def test_sort_by_upload_date(self):
        algo1 = Algorithm.objects.create(name="name_c")
        algo2 = Algorithm.objects.create(name="name_a")
        algo3 = Algorithm.objects.create(name="name_b")
        url = reverse("algorithm_overview_sorted", args=("upload_date",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo1, algo2, algo3])


def upload_algorithm(client, name, group, description, file_name):
    path = f"tests/sample_algorithms/{file_name}"
    with open(path, "r") as file:
        data = {
            "name": name,
            "group": group,
            "description": description,
            "path": file
        }

        return client.post(reverse("algorithm_upload"), data=data, follow=True)


class AlgorithmUploadViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().setUpClass()

    def setUp(self) -> None:
        self.credentials = {
            "username": "user",
            "password": "passwd"
        }
        user = User.objects.create_user(**self.credentials)
        self.user_id = user.pk
        self.client.post(reverse("login"), self.credentials, follow=True)
        super().setUp()

    def tearDown(self) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def test_valid_upload(self):
        test_name = "Test Valid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Valid Description"
        test_file_name = "SampleAlgorithmValid.py"
        response = upload_algorithm(self.client, test_name, test_group, test_description, test_file_name)

        self.assertEqual(response.status_code, 200)
        # we expect to be redirected to algorithm_overview
        self.assertEqual(response.resolver_match.url_name, "algorithm_overview_sorted")
        self.assertTrue(response.redirect_chain)

        algorithm = Algorithm.objects.get()
        self.assertEqual(algorithm.name, test_name)
        self.assertEqual(algorithm.group, test_group)
        self.assertEqual(algorithm.description, test_description)
        self.assertEqual(str(algorithm.path), f"algorithms/user_{self.user_id}/" + test_file_name)

    def test_algorithm_not_subclass(self):
        test_name = "Test Invalid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Invalid Description"
        test_file_name = "SampleAlgorithmInvalid.py"
        response = upload_algorithm(self.client, test_name, test_group, test_description, test_file_name)

        self.assertEqual(response.status_code, 200)
        # we expect to stay on site
        self.assertFalse(response.redirect_chain)
        self.assertContains(response, "is not a subclass of pyod.models.base.BaseDetector")

        algorithm = Algorithm.objects.first()
        self.assertIsNone(algorithm)
        self.assertFalse(os.path.exists(f"algorithms/{self.user_id}/" + test_file_name))

    def test_algorithm_no_class(self):
        test_name = "Test Invalid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Invalid Description"
        test_file_name = "SampleAlgorithmNoClass.py"
        response = upload_algorithm(self.client, test_name, test_group, test_description, test_file_name)

        self.assertEqual(response.status_code, 200)
        # we expect to stay on site
        self.assertFalse(response.redirect_chain)
        self.assertContains(response, "file does not contain a class of the same name")

        algorithm = Algorithm.objects.first()
        self.assertIsNone(algorithm)
        self.assertFalse(os.path.exists(f"algorithms/{self.user_id}/" + test_file_name))


class AlgorithmDeleteViewTests(TestCase):

    def setUp(self) -> None:
        self.credentials = {
            "username": "user",
            "password": "passwd"
        }
        user = User.objects.create_user(**self.credentials)
        self.client.post(reverse("login"), self.credentials, follow=True)
        super(AlgorithmDeleteViewTests, self).setUp()

    def test_delete(self):
        algorithm = Algorithm.objects.create()
        response = self.client.post(reverse("algorithm_delete", args=(algorithm.pk,)))
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(Algorithm.objects.first())

    @skip
    def test_delete_invalid_pk(self):
        response = self.client.post(reverse("algorithm_delete", args=(42,)))
        # we expect to be redirected to the algorithm overview
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(Algorithm.objects.first())
