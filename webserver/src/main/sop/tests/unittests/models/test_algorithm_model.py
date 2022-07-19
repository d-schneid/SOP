from django.test import TestCase

from experiments.models import Algorithm


class AlgorithmModelTests(TestCase):
    def setUp(self) -> None:
        self.algo1 = Algorithm.objects.create(signature="")
        self.algo2 = Algorithm.objects.create(signature="")
        self.algo3 = Algorithm.objects.create(signature="")

    def test_algorithm_model(self):
        pass
