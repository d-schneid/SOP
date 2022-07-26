from experiments.models import Algorithm
from tests.unittests.views.LoggedInTestCase import DjangoTestCase


class AlgorithmModelTests(DjangoTestCase):
    def setUp(self) -> None:
        self.algo1 = Algorithm.objects.create(signature="")
        self.algo2 = Algorithm.objects.create(signature="")
        self.algo3 = Algorithm.objects.create(signature="")

    def test_algorithm_model(self):
        pass
