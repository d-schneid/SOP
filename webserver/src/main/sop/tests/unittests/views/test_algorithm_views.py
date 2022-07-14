import os
import shutil

from django.conf import settings
from django.urls import reverse

from experiments.models import Algorithm
from tests.unittests.views.LoggedInTestCase import LoggedInTestCase


class AlgorithmOverviewTests(LoggedInTestCase):
    def setUp(self) -> None:
        self.QUERYSET_NAME = "models_list"
        super().setUp()

    def test_algorithm_overview_no_algorithms(self):
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [])

    def test_algorithm_overview_one_algorithm(self):
        algorithm = Algorithm.objects.create(display_name="test_algo", user=self.user)
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertContains(response, "test_algo")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algorithm])

    def test_algorithm_overview_multiple_algorithms(self):
        algo1 = Algorithm.objects.create(display_name="name_b", user=self.user)
        algo2 = Algorithm.objects.create(display_name="name_a", user=self.user)
        algo3 = Algorithm.objects.create(display_name="name_c", user=self.user)
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(
            response.context[self.QUERYSET_NAME], [algo2, algo1, algo3]
        )

    def test_algorithm_overview_sort_by_group(self):
        algo1 = Algorithm.objects.create(
            group=Algorithm.AlgorithmGroup.PROBABILISTIC, user=self.user
        )
        algo2 = Algorithm.objects.create(
            group=Algorithm.AlgorithmGroup.COMBINATION, user=self.user
        )
        algo3 = Algorithm.objects.create(
            group=Algorithm.AlgorithmGroup.LINEAR_MODEL, user=self.user
        )
        url = reverse("algorithm_overview_sorted", args=("group",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertContains(response, Algorithm.AlgorithmGroup.PROBABILISTIC)
        self.assertContains(response, Algorithm.AlgorithmGroup.COMBINATION)
        self.assertContains(response, Algorithm.AlgorithmGroup.LINEAR_MODEL)
        self.assertQuerysetEqual(
            response.context[self.QUERYSET_NAME], [algo2, algo3, algo1]
        )

    def test_algorithm_overview_sort_by_upload_date(self):
        algo1 = Algorithm.objects.create(display_name="name_c", user=self.user)
        algo2 = Algorithm.objects.create(display_name="name_a", user=self.user)
        algo3 = Algorithm.objects.create(display_name="name_b", user=self.user)
        url = reverse("algorithm_overview_sorted", args=("upload_date",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(
            response.context[self.QUERYSET_NAME], [algo3, algo2, algo1]
        )

    def test_algorithm_overview_do_not_display_public_algorithms(self):
        algo1 = Algorithm.objects.create(display_name="name_c", user=self.user)
        Algorithm.objects.create(display_name="name_a")
        algo2 = Algorithm.objects.create(display_name="name_b", user=self.user)
        Algorithm.objects.create(display_name="name_d")
        url = reverse("algorithm_overview_sorted", args=("name",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertNotContains(response, "name_a")
        self.assertNotContains(response, "name_d")
        self.assertQuerysetEqual(response.context[self.QUERYSET_NAME], [algo2, algo1])


def upload_algorithm(client, name, group, description, file_name):
    path = f"tests/sample_algorithms/{file_name}"
    with open(path, "r") as file:
        data = {
            "display_name": name,
            "group": group,
            "description": description,
            "path": file,
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

    def test_algorithm_upload_view_valid_upload(self):
        test_name = "Test Valid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Valid Description"
        test_file_name = "SampleAlgorithmValid.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, "algorithm_upload.html")
        self.assertTemplateUsed(response, "algorithm_overview.html")
        # we expect to be redirected to algorithm_overview
        self.assertEqual(response.resolver_match.url_name, "algorithm_overview_sorted")
        self.assertTrue(response.redirect_chain)

        algorithm = Algorithm.objects.get()
        self.assertEqual(self.user, algorithm.user)
        self.assertEqual(algorithm.display_name, test_name)
        self.assertEqual(algorithm.group, test_group)
        self.assertEqual(algorithm.description, test_description)
        self.assertEqual(
            str(algorithm.path), f"algorithms/user_{self.user.pk}/" + test_file_name
        )

    def test_algorithm_upload_view_not_subclass(self):
        test_name = "Test Invalid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Invalid Description"
        test_file_name = "SampleAlgorithmInvalid.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_upload.html")
        self.assertTemplateNotUsed(response, "algorithm_overview.html")
        # we expect to stay on site
        self.assertFalse(response.redirect_chain)
        self.assertContains(
            response, "is not a subclass of pyod.models.base.BaseDetector"
        )

        algorithm = Algorithm.objects.first()
        self.assertIsNone(algorithm)
        self.assertFalse(os.path.exists(f"algorithms/{self.user.pk}/" + test_file_name))

    def test_algorithm_upload_view_no_class(self):
        test_name = "Test Invalid Algorithm"
        test_group = Algorithm.AlgorithmGroup.COMBINATION
        test_description = "Test Invalid Description"
        test_file_name = "SampleAlgorithmNoClass.py"
        response = upload_algorithm(
            self.client, test_name, test_group, test_description, test_file_name
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "algorithm_upload.html")
        self.assertTemplateNotUsed(response, "algorithm_overview.html")
        # we expect to stay on site
        self.assertFalse(response.redirect_chain)
        self.assertContains(response, "file does not contain a class of the same name")

        algorithm = Algorithm.objects.first()
        self.assertIsNone(algorithm)
        self.assertFalse(os.path.exists(f"algorithms/{self.user.pk}/" + test_file_name))


class AlgorithmDeleteViewTests(LoggedInTestCase):
    def test_algorithm_delete_view_valid_delete(self):
        algorithm = Algorithm.objects.create()
        response = self.client.post(
            reverse("algorithm_delete", args=(algorithm.pk,)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertIsNone(Algorithm.objects.first())
        self.assertTemplateUsed(response, "algorithm_overview.html")

    def test_algorithm_delete_view_invalid_pk(self):
        response = self.client.post(
            reverse("algorithm_delete", args=(42,)), follow=True
        )
        # we expect to be redirected to the algorithm overview
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, "algorithm_overview.html")


class AlgorithmEditViewTest(LoggedInTestCase):
    def post_algorithm_edit(
        self, algorithm_pk=None, expected_code=200, update_model=True
    ):
        algorithm_pk = algorithm_pk if algorithm_pk is not None else self.algo.pk
        data = {
            "display_name": self.new_name,
            "description": self.new_description,
            "group": self.new_group,
        }
        response = self.client.post(
            reverse("algorithm_edit", args=(algorithm_pk,)), follow=True, data=data
        )
        self.assertEqual(response.status_code, expected_code)
        # reload algorithm from db
        if update_model:
            self.algo = Algorithm.objects.get(pk=algorithm_pk)
        return response

    def assertNoAlgorithmChange(self, response):
        self.assertFalse(response.redirect_chain)
        self.assertEqual(self.name, self.algo.display_name)
        self.assertEqual(self.description, self.algo.description)
        self.assertEqual(self.group, self.algo.group)

    def assertAlgorithmChange(self, response):
        self.assertTrue(response.redirect_chain)
        self.assertEqual(self.new_name, self.algo.display_name)
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
        self.algo = Algorithm.objects.create(
            display_name=self.name,
            group=self.group,
            description=self.description,
            user=self.user,
        )

    def test_algorithm_edit_view_valid_edit(self):
        response = self.post_algorithm_edit()
        self.assertTemplateNotUsed(response, "algorithm_edit.html")
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertAlgorithmChange(response)

    def test_algorithm_edit_view_edit_no_name(self):
        self.new_name = ""
        response = self.post_algorithm_edit()
        self.assertTemplateUsed(response, "algorithm_edit.html")
        self.assertTemplateNotUsed(response, "algorithm_overview.html")
        self.assertNoAlgorithmChange(response)

    def test_algorithm_edit_view_edit_no_group(self):
        self.new_group = ""
        response = self.post_algorithm_edit()
        self.assertTemplateUsed(response, "algorithm_edit.html")
        self.assertTemplateNotUsed(response, "algorithm_overview.html")
        self.assertNoAlgorithmChange(response)

    def test_algorithm_edit_view_edit_no_description(self):
        self.new_description = ""
        response = self.post_algorithm_edit()
        self.assertTemplateNotUsed(response, "algorithm_edit.html")
        self.assertTemplateUsed(response, "algorithm_overview.html")
        self.assertAlgorithmChange(response)

    def test_algorithm_edit_view_edit_invalid_pk(self):
        response = self.post_algorithm_edit(
            algorithm_pk=42, expected_code=404, update_model=False
        )
        self.assertTemplateNotUsed(response, "algorithm_edit.html")
        self.assertTemplateNotUsed(response, "algorithm_overview.html")
        self.assertNoAlgorithmChange(response)
