import unittest
from multiprocessing.shared_memory import SharedMemory

import numpy as np

from backend.task.execution.subspace.Subspace import Subspace


class UnitTestSubspace(unittest.TestCase):
    basic_methods_para = [
        ([True], 1, 1, "g"),
        ([True, False, True], 2, 3, "o"),
        ([True, True, True, True, True, False, False], 5, 7, "-A"),
        ([True, False, True, True, False, False,
          False, False, True, False], 4, 10, "sI")
        # Example from our system requirements specification
    ]

    def test_basic_methods(self):
        for mask, ss_dim_count, ds_dim_count, ss_ident in self.basic_methods_para:
            ss = Subspace(np.array(mask))
            self.assertEqual(ss_dim_count, ss.get_included_dimension_count())
            self.assertEqual(ds_dim_count, ss.get_dataset_dimension_count())
            self.assertEqual(ss_ident, ss.get_subspace_identifier())

    subspace_arrays_para = [
        (np.array([[1, 2], [3, 4]], dtype=np.dtype('i2')),
         [True, False], 4,
         np.array([[1], [3]], dtype=np.dtype('i2')))
    ]

    def test_subspace_arrays(self):
        for ds_arr, mask, exp_ss_arr_sz, exp_ss_arr in self.subspace_arrays_para:
            ss = Subspace(np.array(mask))
            ss_arr_sz = ss.get_size_of_subspace_buffer(ds_arr)
            self.assertEqual(exp_ss_arr_sz, ss_arr_sz)
            shm = None
            try:
                shm = SharedMemory(None, True, ss_arr_sz)
                ss_arr = ss.make_subspace_array(ds_arr, shm)
                self.assertTrue(np.array_equal(exp_ss_arr, ss_arr))
                # check that array is really in shm
                shm.buf[0] = shm.buf[0] ^ 0b11111111
                self.assertFalse(np.array_equal(exp_ss_arr, ss_arr))
            finally:
                shm.unlink()
                shm.close()


if __name__ == '__main__':
    unittest.main()
