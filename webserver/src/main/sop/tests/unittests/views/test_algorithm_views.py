import os
import shutil
from unittest import skip

from django.urls import reverse

from experiments.models import Algorithm
from django.conf import settings

from tests.unittests.views.LoggedInTestCase import LoggedInTestCase


class AlgorithmOverviewTests(LoggedInTestCase):

    def setUp(self) -> None:
        self.QUERYSET_NAME = "models_list"
        super().setUp()

    def test_no_algorithms(self):
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [])

    def test_one_algorithm(self):
        algorithm = Algorithm.objects.create(name="test_algo", user=self.user)
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_algo")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algorithm])

    def test_multiple_algorithms(self):
        algo1 = Algorithm.objects.create(name="name_b", user=self.user)
        algo2 = Algorithm.objects.create(name="name_a", user=self.user)
        algo3 = Algorithm.objects.create(name="name_c", user=self.user)
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo2, algo1, algo3])

    def test_sort_by_group(self):
        algo1 = Algorithm.objects.create(group=Algorithm.AlgorithmGroup.PROBABILISTIC, user=self.user)
        algo2 = Algorithm.objects.create(group=Algorithm.AlgorithmGroup.COMBINATION, user=self.user)
        algo3 = Algorithm.objects.create(group=Algorithm.AlgorithmGroup.LINEAR_MODEL, user=self.user)
        url = reverse("algorithm_overview_sorted", args=("group",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Algorithm.AlgorithmGroup.PROBABILISTIC)
        self.assertContains(response, Algorithm.AlgorithmGroup.COMBINATION)
        self.assertContains(response, Algorithm.AlgorithmGroup.LINEAR_MODEL)
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo2, algo3, algo1])

    def test_sort_by_upload_date(self):
        algo1 = Algorithm.objects.create(name="name_c", user=self.user)
        algo2 = Algorithm.objects.create(name="name_a", user=self.user)
        algo3 = Algorithm.objects.create(name="name_b", user=self.user)
        url = reverse("algorithm_overview_sorted", args=("upload_date",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo3, algo2, algo1])

    def test_do_not_display_public_algorithms(self):
        algo1 = Algorithm.objects.create(name="name_c", user=self.user)
        Algorithm.objects.create(name="name_a")
        algo2 = Algorithm.objects.create(name="name_b", user=self.user)
        Algorithm.objects.create(name="name_d")
        url = reverse("algorithm_overview_sorted", args=("name",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertNotContains(response, "name_a")
        self.assertNotContains(response, "name_d")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo2, algo1])


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


class AlgorithmUploadViewTests(LoggedInTestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().setUpClass()

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
        self.assertEqual(str(algorithm.path), f"algorithms/user_{self.user.pk}/" + test_file_name)

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
        self.assertFalse(os.path.exists(f"algorithms/{self.user.pk}/" + test_file_name))

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
        self.assertFalse(os.path.exists(f"algorithms/{self.user.pk}/" + test_file_name))


class AlgorithmDeleteViewTests(LoggedInTestCase):

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


class AlgorithmEditViewTest(LoggedInTestCase):
    def post_algorithm_edit(self):
        data = {
            "name": self.new_name,
            "description": self.new_description,
            "group": self.new_group,
        }
        response = self.client.post(reverse("algorithm_edit", args=(self.algo.pk,)), follow=True, data=data)
        self.assertEqual(response.status_code, 200)
        # reload algorithm from db
        self.algo = Algorithm.objects.get(pk=self.algo.pk)
        return response

    def assertNoAlgorithmChange(self, response):
        self.assertFalse(response.redirect_chain)
        self.assertEqual(self.name, self.algo.name)
        self.assertEqual(self.description, self.algo.description)
        self.assertEqual(self.group, self.algo.group)

    def assertAlgorithmChange(self, response):
        self.assertTrue(response.redirect_chain)
        self.assertEqual(self.new_name, self.algo.name)
        self.assertEqual(self.new_description, self.algo.description)
        self.assertEqual(self.new_group, self.algo.group)

    def setUp(self) -> None:
        self.name = "Original Name"
        self.group = Algorithm.AlgorithmGroup.COMBINATION
        self.description = "Original Description"
        self.new_name = "New Name"
        self.new_description = "New Description"
        self.new_group = Algorithm.AlgorithmGroup.PROBABILISTIC
        super().setUp()
        self.algo = Algorithm.objects.create(name=self.name, group=self.group,
                                        description=self.description, user=self.user)

    def test_valid_edit(self):
        response = self.post_algorithm_edit()
        self.assertAlgorithmChange(response)

    def test_edit_no_name(self):
        self.new_name = ""
        response = self.post_algorithm_edit()
        self.assertNoAlgorithmChange(response)

    def test_edit_no_group(self):
        self.new_group = ""
        response = self.post_algorithm_edit()
        self.assertNoAlgorithmChange(response)

    def test_edit_no_description(self):
        self.new_description = ""
        response = self.post_algorithm_edit()
        self.assertAlgorithmChange(response)
