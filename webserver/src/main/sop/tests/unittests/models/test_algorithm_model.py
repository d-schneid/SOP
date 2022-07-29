from experiments.models import Algorithm
from tests.unittests.views.generic_test_cases import DebugSchedulerTestCase


class AlgorithmModelTests(DebugSchedulerTestCase):
    def setUp(self) -> None:
        self.algo1 = Algorithm.objects.create(signature="")
        self.algo2 = Algorithm.objects.create(signature="")
        self.algo3 = Algorithm.objects.create(signature="")

    def test_algorithm_model(self) -> None:
        pass
