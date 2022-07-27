import json
import os
import shutil
from typing import Optional, Dict, Any

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy

from experiments.models import Experiment, Dataset, Algorithm
from tests.unittests.views.generic_test_cases import LoggedInTestCase


class ExperimentOverviewTests(LoggedInTestCase):
    def setUp(self) -> None:
        self.QUERYSET_NAME: str = "models_list"
        super().setUp()

    def create_experiment(self, name: str) -> Experiment:
        dataset = Dataset.objects.create(
            display_name="Datset Name",
            description="Dataset Description",
            user=self.user,
            datapoints_total=4,
            dimensions_total=7,
        )
        algo1 = Algorithm.objects.create(
            display_name="First Algorithm",
            group=Algorithm.AlgorithmGroup.PROBABILISTIC,
            user=self.user,
            signature="",
        )
        algo2 = Algorithm.objects.create(
            display_name="Second Algorithm",
            group=Algorithm.AlgorithmGroup.COMBINATION,
            user=self.user,
            signature="",
        )
        exp = Experiment.objects.create(
            display_name=name, user=self.user, dataset=dataset
        )
        exp.algorithms.set([algo1, algo2])
        return exp

    def test_experiment_overview_no_experiments(self) -> None:
        response = self.client.get(reverse("experiment_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_overview.html")
        self.assertListEqual(list(response.context[self.QUERYSET_NAME]), [])  # type: ignore

    def test_experiment_overview_one_experiment(self) -> None:
        experiment = self.create_experiment("test_experiment")
        response = self.client.get(reverse("experiment_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_overview.html")
        self.assertContains(response, "test_experiment")
        self.assertListEqual(list(response.context[self.QUERYSET_NAME]), [experiment])  # type: ignore

    def test_experiment_overview_multiple_experiments(self) -> None:
        experiment1 = self.create_experiment("name_b")
        experiment2 = self.create_experiment("name_a")
        experiment3 = self.create_experiment("name_c")
        response = self.client.get(reverse("experiment_overview"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_overview.html")
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertListEqual(
            list(response.context[self.QUERYSET_NAME]),  # type: ignore
            [experiment2, experiment1, experiment3],
        )

    def test_experiment_overview_sort_by_upload_date(self) -> None:
        experiment1 = self.create_experiment("name_c")
        experiment2 = self.create_experiment("name_a")
        experiment3 = self.create_experiment("name_b")
        url = reverse("experiment_overview_sorted", args=("creation_date",))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_overview.html")
        self.assertContains(response, "name_a")
        self.assertContains(response, "name_b")
        self.assertContains(response, "name_c")
        self.assertListEqual(
            list(response.context[self.QUERYSET_NAME]),  # type: ignore
            [experiment3, experiment2, experiment1],
        )


class ExperimentCreateViewTests(LoggedInTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().setUpClass()

    def setUp(self) -> None:
        # do this before, so we have access to self.user later
        super().setUp()
        self.name = "Test Valid Dataset"
        self.dataset = Dataset.objects.create(
            display_name="Datset Name",
            description="Dataset Description",
            user=self.user,
            datapoints_total=4,
            dimensions_total=7,
        )
        self.algorithms = [
            Algorithm.objects.create(
                display_name="First Algorithm",
                group=Algorithm.AlgorithmGroup.PROBABILISTIC,
                user=self.user,
                signature="",
            ),
            Algorithm.objects.create(
                display_name="Second Algorithm",
                group=Algorithm.AlgorithmGroup.COMBINATION,
                user=self.user,
                signature="",
            ),
        ]

    def tearDown(self) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def post_experiment_creation(self) -> HttpResponse:
        data = {
            "display_name": self.name,
            # we need to pass in the primary keys since these are choice fields and datasets and algorithms are
            # passed via their primary key
            "dataset": self.dataset.pk,
            "check-algo": [algo.pk for algo in self.algorithms],
        }
        return self.client.post(  # type:ignore
            reverse("experiment_create"), data=data, follow=True
        )

    def test_experiment_create_view_valid_creation(self) -> None:
        response = self.post_experiment_creation()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, "experiment_create.html")
        self.assertTemplateUsed(response, "experiment_overview.html")
        # we expect to be redirected to experiment_overview
        self.assertEqual("experiment_overview_sorted", response.resolver_match.url_name)  # type: ignore
        self.assertTrue(response.redirect_chain)

        experiment = Experiment.objects.get()
        self.assertEqual(self.user, experiment.user)
        self.assertEqual(self.name, experiment.display_name)
        self.assertEqual(self.dataset, experiment.dataset)
        self.assertEqual(self.algorithms, list(experiment.algorithms.all()))

    def test_experiment_create_view_no_algorithms(self) -> None:
        self.algorithms = []
        response = self.post_experiment_creation()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experiment_create.html")
        self.assertTemplateNotUsed(response, "experiment_overview.html")
        # we expect to stay on the experiment_upload
        self.assertFalse(response.redirect_chain)
        experiment = Experiment.objects.first()
        self.assertIsNone(experiment)


class ExperimentEditViewTests(LoggedInTestCase):
    def setUp(self) -> None:
        self.name = "Original Name"
        self.new_name = "New Name"
        super().setUp()
        self.dataset = Dataset.objects.create(
            display_name="Datset Name",
            description="Dataset Description",
            user=self.user,
            datapoints_total=4,
            dimensions_total=7,
        )
        self.algorithms = [
            Algorithm.objects.create(
                display_name="First Algorithm",
                group=Algorithm.AlgorithmGroup.PROBABILISTIC,
                user=self.user,
                signature="",
            ),
            Algorithm.objects.create(
                display_name="Second Algorithm",
                group=Algorithm.AlgorithmGroup.COMBINATION,
                user=self.user,
                signature="",
            ),
        ]
        self.experiment = Experiment.objects.create(
            display_name=self.name, user=self.user, dataset=self.dataset
        )
        self.experiment.algorithms.set(self.algorithms)

    def post_experiment_edit(
        self,
        experiment_pk: Optional[int] = None,
        expected_status: int = 200,
        update_model: bool = True,
    ) -> HttpResponse:
        experiment_pk = (
            experiment_pk if experiment_pk is not None else self.experiment.pk
        )
        data = {
            "display_name": self.new_name,
        }
        response = self.client.post(
            reverse("experiment_edit", args=(experiment_pk,)), follow=True, data=data
        )
        self.assertEqual(response.status_code, expected_status)
        # reload experiment from db
        if update_model:
            self.experiment = Experiment.objects.get(pk=experiment_pk)
        return response  # type: ignore

    def assertNoExperimentChange(self, response: HttpResponse) -> None:
        self.assertFalse(response.redirect_chain)
        self.assertEqual(self.name, self.experiment.display_name)
        self.assertEqual(self.user, self.experiment.user)

    def assertExperimentChange(self, response: HttpResponse) -> None:
        self.assertTrue(response.redirect_chain)
        self.assertEqual(self.new_name, self.experiment.display_name)
        self.assertEqual(self.user, self.experiment.user)

    def test_experiment_edit_view_valid_edit(self) -> None:
        response = self.post_experiment_edit()
        self.assertTemplateNotUsed(response, "experiment_edit.html")
        self.assertTemplateUsed(response, "experiment_overview.html")
        self.assertExperimentChange(response)

    def test_experiment_edit_view_edit_no_name(self) -> None:
        self.new_name = ""
        response = self.post_experiment_edit()
        self.assertTemplateUsed(response, "experiment_edit.html")
        self.assertTemplateNotUsed(response, "experiment_overview.html")
        self.assertNoExperimentChange(response)

    def test_experiment_edit_view_edit_invalid_pk(self) -> None:
        response = self.post_experiment_edit(
            experiment_pk=42, expected_status=404, update_model=False
        )
        self.assertTemplateNotUsed(response, "experiment_edit.html")
        self.assertTemplateNotUsed(response, "experiment_overview.html")
        self.assertNoExperimentChange(response)


class ExperimentDeleteViewTests(LoggedInTestCase):
    def test_experiment_delete_view_valid_delete(self) -> None:
        dataset = Dataset.objects.create(
            datapoints_total=0, dimensions_total=0, user=self.user
        )
        algo = Algorithm.objects.create(signature="")
        experiment = Experiment.objects.create(dataset=dataset, user=self.user)
        experiment.algorithms.set([algo])
        experiment.save()
        response = self.client.post(
            reverse("experiment_delete", args=(experiment.pk,)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)  # type: ignore
        self.assertIsNone(Experiment.objects.first())
        self.assertTemplateUsed(response, "experiment_overview.html")

    def test_experiment_delete_view_invalid_pk(self) -> None:
        response = self.client.post(
            reverse("experiment_delete", args=(42,)), follow=True
        )
        # we expect to be redirected to the experiment overview
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)  # type: ignore
        self.assertTemplateUsed(response, "experiment_overview.html")


class ExperimentDuplicateViewTests(LoggedInTestCase):
    dataset: Dataset
    algo1: Algorithm
    algo2: Algorithm
    exp: Experiment
    data: Dict[str, Any]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.dataset = Dataset.objects.create(user=cls.user, dimensions_total=10)
        cls.exp = Experiment.objects.create(
            dataset=cls.dataset, user=cls.user, display_name="HUHU"
        )
        cls.algo1 = Algorithm.objects.create(
            display_name="Algo 1",
            signature=json.dumps({"param1": 5, "param2": "Hello"}),
            group=Algorithm.AlgorithmGroup.COMBINATION,
        )
        cls.algo2 = Algorithm.objects.create(
            display_name="Algo 2",
            signature=json.dumps({"param1": 4.8, "param2": None}),
            group=Algorithm.AlgorithmGroup.PROBABILISTIC,
        )
        cls.exp.algorithms.set([cls.algo1])  # noqa

    def test_experiment_duplicate_view(self) -> None:
        response = self.client.get(
            reverse_lazy("experiment_duplicate", args=(self.exp.pk,)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.redirect_chain)  # type: ignore
        self.assertTemplateUsed("experiment_create")

        self.assertContains(response, "HUHU")

        # Not really checks for if they are selected, but it still has to be there, so we might as well check it
        self.assertContains(response, self.algo1.display_name)
        self.assertContains(response, self.algo2.display_name)
        self.assertContains(response, self.algo1.group)
        self.assertContains(response, self.algo2.group)
