from django.test import TestCase
from django.urls import reverse

from authentication.models import User
from experiments.models import Algorithm

QUERYSET_NAME = "models_list"


class AlgorithmOverviewTests(TestCase):

    def setUp(self) -> None:
        self.credentials = {
            "username": "user",
            "password": "passwd"
        }
        User.objects.create_user(**self.credentials)
        self.client.post(reverse("login"), self.credentials, follow=True)

    def test_no_algorithms(self):
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context[QUERYSET_NAME], [])

    def test_one_algorithm(self):
        algorithm = Algorithm.objects.create(name="test_algo")
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_algo")
        self.assertQuerysetEqual(response.context[QUERYSET_NAME], [algorithm])

    def test_multiple_algorithms(self):
        algo1 = Algorithm.objects.create(name="name_b")
        algo2 = Algorithm.objects.create(name="name_a")
        algo3 = Algorithm.objects.create(name="name_c")
        response = self.client.get(reverse("algorithm_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertQuerysetEqual(response.context[QUERYSET_NAME], [algo2, algo1, algo3])

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
        self.assertQuerysetEqual(response.context[QUERYSET_NAME], [algo2, algo3, algo1])

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
        self.assertQuerysetEqual(response.context[QUERYSET_NAME], [algo1, algo2, algo3])
