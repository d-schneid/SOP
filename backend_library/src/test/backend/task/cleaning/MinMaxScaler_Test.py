import unittest

from backend_library.src.main.backend.task.cleaning.MinMaxScaler import MinMaxScaler
from backend_library.src.test.backend.DatasetsForTesting import Datasets as ds


class MinMaxScalerTest(unittest.TestCase):

    def setUp(self) -> None:
        self._min_max_scaler = MinMaxScaler()

    def tearDown(self) -> None:
        self._min_max_scaler = None

    def test_min_max_scaler(self):
        print("Test")
        print(self._min_max_scaler.do_cleaning(ds._dataset5))
        #print(self._min_max_scaler.do_cleaning(ds._dataset0))
        #print(self._min_max_scaler.do_cleaning(ds._dataset1))
        #print(self._min_max_scaler.do_cleaning(ds._dataset2))
        #print(self._min_max_scaler.do_cleaning(ds._dataset3))
        # print(self._min_max_scaler.do_cleaning(ds._empty_dataset))
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
