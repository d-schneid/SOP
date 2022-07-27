import django.test

from authentication.models import User
from experiments.models import Algorithm, Dataset, Experiment, Execution


class AlgorithmQuerySetTests(django.test.TestCase):
    user1: User
    user2: User
    algo1: Algorithm
    algo2: Algorithm
    algo3: Algorithm
    algo4: Algorithm
    algo5: Algorithm

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create(username="1", password="pswd")
        cls.user2 = User.objects.create(username="2", password="pswd")
        cls.algo1 = Algorithm.objects.create(
            signature="",
            user=cls.user1,
            display_name="A",
            group=Algorithm.AlgorithmGroup.COMBINATION,
        )
        cls.algo2 = Algorithm.objects.create(
            signature="",
            user=cls.user1,
            display_name="B",
            group=Algorithm.AlgorithmGroup.PROBABILISTIC,
        )
        cls.algo3 = Algorithm.objects.create(
            signature="",
            user=cls.user2,
            display_name="D",
            group=Algorithm.AlgorithmGroup.PROBABILISTIC,
        )
        cls.algo4 = Algorithm.objects.create(
            signature="",
            user=cls.user2,
            display_name="C",
            group=Algorithm.AlgorithmGroup.PROXIMITY_BASED,
        )
        cls.algo5 = Algorithm.objects.create(
            signature="",
            display_name="Public",
            group=Algorithm.AlgorithmGroup.OTHER,
        )

    def test_algorithm_queryset_get_public(self) -> None:
        queryset = Algorithm.objects.get_public()  # type: ignore
        self.assertListEqual(list(queryset), [self.algo5])

    def test_algorithm_queryset_get_by_user(self) -> None:
        queryset = Algorithm.objects.get_by_user(self.user1)  # type: ignore
        self.assertListEqual(list(queryset), [self.algo1, self.algo2])

    def test_algorithm_queryset_get_by_user_and_public(self) -> None:
        queryset = Algorithm.objects.get_by_user_and_public(self.user1)  # type: ignore
        self.assertListEqual(list(queryset), [self.algo1, self.algo2, self.algo5])

    def test_algorithm_queryset_sorted_by_name(self) -> None:
        queryset = Algorithm.objects.get_sorted_by_name()  # type: ignore
        self.assertListEqual(
            list(queryset), [self.algo1, self.algo2, self.algo4, self.algo3, self.algo5]
        )

    def test_algorithm_queryset_sorted_by_upload_date(self) -> None:
        queryset = Algorithm.objects.get_sorted_by_upload_date()  # type: ignore
        self.assertListEqual(
            list(queryset),
            [self.algo5, self.algo4, self.algo3, self.algo2, self.algo1],
        )

    def test_algorithm_queryset_sorted_by_group_and_name(self) -> None:
        queryset = Algorithm.objects.get_sorted_by_group_and_name()  # type: ignore
        self.assertListEqual(
            list(queryset), [self.algo1, self.algo5, self.algo2, self.algo3, self.algo4]
        )

    def test_algorithm_queryset_get_with_group(self) -> None:
        queryset = Algorithm.objects.get_with_group(Algorithm.AlgorithmGroup.COMBINATION)  # type: ignore
        self.assertListEqual(list(queryset), [self.algo1])

        queryset2 = Algorithm.objects.get_with_group(Algorithm.AlgorithmGroup.NEURAL_NETWORKS)  # type: ignore
        self.assertListEqual(list(queryset2), [])


class DatasetQuerySetTests(django.test.TestCase):
    user1: User
    user2: User
    dataset1: Dataset
    dataset2: Dataset
    dataset3: Dataset
    dataset4: Dataset
    dataset5: Dataset

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create(username="1", password="pswd")
        cls.user2 = User.objects.create(username="2", password="pswd")
        cls.dataset1 = Dataset.objects.create(user=cls.user1, display_name="A")
        cls.dataset2 = Dataset.objects.create(
            user=cls.user1,
            display_name="B",
        )
        cls.dataset3 = Dataset.objects.create(
            user=cls.user2,
            display_name="D",
        )
        cls.dataset4 = Dataset.objects.create(
            user=cls.user2,
            display_name="C",
        )
        cls.dataset5 = Dataset.objects.create(
            user=cls.user2,
            display_name="Z",
        )

    def test_dataset_queryset_get_sorted_by_name(self) -> None:
        queryset = Dataset.objects.get_sorted_by_name()  # type: ignore
        self.assertListEqual(
            list(queryset),
            [self.dataset1, self.dataset2, self.dataset4, self.dataset3, self.dataset5],
        )

    def test_dataset_queryset_get_by_user(self) -> None:
        queryset = Dataset.objects.get_by_user(self.user1)  # type: ignore
        self.assertListEqual(
            list(queryset),
            [self.dataset1, self.dataset2],
        )

        queryset2 = Dataset.objects.get_by_user(self.user2)  # type: ignore
        self.assertListEqual(
            list(queryset2),
            [self.dataset3, self.dataset4, self.dataset5],
        )

    def test_dataset_queryset_get_sorted_by_upload_date(self) -> None:
        queryset = Dataset.objects.get_sorted_by_upload_time()  # type: ignore
        self.assertListEqual(
            list(queryset),
            [self.dataset5, self.dataset4, self.dataset3, self.dataset2, self.dataset1],
        )


class ExperimentQuerySetTests(django.test.TestCase):
    user1: User
    user2: User
    dataset1: Dataset
    dataset2: Dataset
    exp1: Experiment
    exp2: Experiment
    exp3: Experiment
    exp4: Experiment
    exp5: Experiment

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create(username="1", password="pswd")
        cls.user2 = User.objects.create(username="2", password="pswd")
        cls.dataset1 = Dataset.objects.create(user=cls.user1, display_name="D1")
        cls.dataset2 = Dataset.objects.create(user=cls.user1, display_name="D2")
        cls.exp1 = Experiment.objects.create(
            user=cls.user1, display_name="A", dataset=cls.dataset1
        )
        cls.exp2 = Experiment.objects.create(
            user=cls.user1, display_name="B", dataset=cls.dataset1
        )
        cls.exp3 = Experiment.objects.create(
            user=cls.user2, display_name="D", dataset=cls.dataset2
        )
        cls.exp4 = Experiment.objects.create(
            user=cls.user2, display_name="C", dataset=cls.dataset2
        )
        cls.exp5 = Experiment.objects.create(
            user=cls.user2, display_name="Z", dataset=cls.dataset2
        )

    def test_experiment_queryset_get_sorted_by_name(self) -> None:
        queryset = Experiment.objects.get_sorted_by_name()  # type: ignore
        self.assertListEqual(
            list(queryset), [self.exp1, self.exp2, self.exp4, self.exp3, self.exp5]
        )

    def test_experiment_queryset_get_sorted_by_creation_date(self) -> None:
        queryset = Experiment.objects.get_sorted_by_creation_date()  # type: ignore
        self.assertListEqual(
            list(queryset), [self.exp5, self.exp4, self.exp3, self.exp2, self.exp1]
        )

    def test_experiment_queryset_get_sorted_by_user(self) -> None:
        queryset = Experiment.objects.get_by_user(self.user1)  # type: ignore
        self.assertListEqual(list(queryset), [self.exp1, self.exp2])

        queryset2 = Experiment.objects.get_by_user(self.user2)  # type: ignore
        self.assertListEqual(list(queryset2), [self.exp3, self.exp4, self.exp5])

    def test_experiment_queryset_get_with_dataset(self) -> None:
        queryset = Experiment.objects.get_with_dataset(self.dataset1)  # type: ignore
        self.assertListEqual(list(queryset), [self.exp1, self.exp2])

        queryset2 = Experiment.objects.get_with_dataset(self.dataset2)  # type: ignore
        self.assertListEqual(list(queryset2), [self.exp3, self.exp4, self.exp5])


class ExecutionQuerySetTests(django.test.TestCase):
    user1: User
    user2: User
    dataset1: Dataset
    exp1: Experiment
    exp2: Experiment
    exe1: Execution
    exe2: Execution
    exe3: Execution
    exe4: Execution

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create(username="1", password="pswd")
        cls.user2 = User.objects.create(username="2", password="pswd")
        cls.dataset1 = Dataset.objects.create(user=cls.user1, display_name="D1")
        cls.exp1 = Experiment.objects.create(
            user=cls.user1, display_name="A", dataset=cls.dataset1
        )
        cls.exp2 = Experiment.objects.create(
            user=cls.user2, display_name="A", dataset=cls.dataset1
        )
        cls.exe1 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=2,
            subspaces_min=1,
            subspaces_max=3,
        )
        cls.exe2 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
        )
        cls.exe3 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp1,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
        )
        cls.exe4 = Execution.objects.create(
            algorithm_parameters="",
            experiment=cls.exp2,
            subspace_amount=4,
            subspaces_min=2,
            subspaces_max=11,
        )

    def test_execution_queryset_get_sorted_by_creation_date(self) -> None:
        queryset = Execution.objects.get_sorted_by_creation_date()  # type: ignore
        self.assertListEqual(
            list(queryset), [self.exe4, self.exe3, self.exe2, self.exe1]
        )

    def test_execution_queryset_get_by_user(self) -> None:
        queryset = Execution.objects.get_by_user(self.user1)  # type: ignore
        self.assertListEqual(list(queryset), [self.exe1, self.exe2, self.exe3])

        queryset2 = Execution.objects.get_by_user(self.user2)  # type: ignore
        self.assertListEqual(list(queryset2), [self.exe4])
