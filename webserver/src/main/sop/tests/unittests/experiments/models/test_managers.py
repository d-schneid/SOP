import django.test

from authentication.models import User
from experiments.models import Algorithm


class ModelManagerTests(django.test.TestCase):
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
        print(queryset)
        self.assertListEqual(
            list(queryset), [self.algo1, self.algo5, self.algo2, self.algo3, self.algo4]
        )

    def test_algorithm_queryset_get_with_group(self) -> None:
        queryset = Algorithm.objects.get_with_group(Algorithm.AlgorithmGroup.COMBINATION)  # type: ignore
        self.assertListEqual(list(queryset), [self.algo1])

        queryset2 = Algorithm.objects.get_with_group(Algorithm.AlgorithmGroup.NEURAL_NETWORKS)  # type: ignore
        self.assertListEqual(list(queryset2), [])
