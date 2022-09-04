import unittest

from backend.task.execution.AlgorithmLoader import AlgorithmLoader as AL

algo_dir = "../resources/test/algorithms/"


class UnitTestAlgorithmLoader(unittest.TestCase):

    def setUp(self) -> None:
        AL.set_algorithm_root_dir("../resources/test")

    def test_basic_loading(self):
        self.assertIsNone(AL.is_algorithm_valid(algo_dir + "DebugAlgorithm.py"))
        algorithm_class = AL.get_algorithm_class(algo_dir + "DebugAlgorithm.py")
        self.assertEqual("DebugAlgorithm", algorithm_class.__name__)
        paras = {"algorithm_result": 2}
        algorithm_obj = AL.get_algorithm_object(algo_dir + "DebugAlgorithm.py", paras)
        self.assertEqual(2, algorithm_obj._algorithm_result)
        algorithm_paras = AL.get_algorithm_parameters(algo_dir + "DebugAlgorithm.py")
        self.assertIn("algorithm_result", algorithm_paras)

    wrongAlgoFiles = ["abc", "WrongAlgorithm.py", "EmptyAlgorithm.py", "NoAlgo.py"]

    def test_errors(self):
        for file in self.wrongAlgoFiles:
            self.assertIsNotNone(AL.is_algorithm_valid(algo_dir + file))


if __name__ == '__main__':
    unittest.main()
