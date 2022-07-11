from django.test import TestCase

from experiments.models import Algorithm


class AlgorithmModelTests(TestCase):
    def setUp(self) -> None:
        self.algo1 = Algorithm.objects.create()
        self.algo2 = Algorithm.objects.create()
        self.algo3 = Algorithm.objects.create()

    def test_algorithm_model(self):
        pass
