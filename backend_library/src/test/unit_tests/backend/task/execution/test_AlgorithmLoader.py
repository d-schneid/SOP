import unittest

from backend.task.execution.AlgorithmLoader import AlgorithmLoader


class UnitTestAlgorithmLoader(unittest.TestCase):
    algo_location = "./test/algorithms/DebugAlgorithm.py"

    def setUp(self) -> None:
        AlgorithmLoader.set_algorithm_root_dir("./test")

    def test_basic_loading(self):
        self.assertIsNone(AlgorithmLoader.is_algorithm_valid(self.algo_location))
        algorithm_class = AlgorithmLoader.get_algorithm_class(self.algo_location)
        self.assertEqual("DebugAlgorithm", algorithm_class.__name__)
        paras = {"algorithm_result": 2}
        algorithm_obj = AlgorithmLoader.get_algorithm_object(self.algo_location, paras)
        self.assertEqual(2, algorithm_obj._algorithm_result[0, 0])
        algorithm_paras = AlgorithmLoader.get_algorithm_parameters(self.algo_location)
        self.assertIn("algorithm_result", algorithm_paras)
        wrongAlgo = "./test/algorithms/WrongAlgorithm.py"
        self.assertIsNotNone(AlgorithmLoader.is_algorithm_valid("abc"))
        self.assertIsNotNone(AlgorithmLoader.is_algorithm_valid(wrongAlgo))

    # def test_(self):


if __name__ == '__main__':
    unittest.main()
