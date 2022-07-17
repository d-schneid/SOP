import unittest
from random import Random

import numpy as np

from backend.task.execution.subspace.RandomizedSubspaceGeneration import \
    RandomizedSubspaceGeneration
from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution


class UnitTestRndSubGen(unittest.TestCase):
    ss_gen_paras = [(2, 2, 1, 1)]

    def test_ss_gen(self):
        for ds_dim_count, ss_count, ss_sz_min, ss_sz_max in self.ss_gen_paras:
            sz_distr = UniformSubspaceDistribution(ss_sz_min, ss_sz_max)
            sd = Random().randint(0, 1000)
            ss_gen1 = RandomizedSubspaceGeneration(sz_distr, ds_dim_count, ss_count, sd)
            ss_gen2 = RandomizedSubspaceGeneration(sz_distr, ds_dim_count, ss_count, sd)
            ss_list1 = ss_gen1.generate()
            ss_list2 = ss_gen1.generate()
            self.assertEqual(ss_count, len(ss_list1))
            for i in range(len(ss_list1)):
                current_ss = ss_list1[i]
                self.assertTrue(np.array_equal(current_ss.mask, ss_list2[i].mask))
                self.assertEqual(ds_dim_count, current_ss.get_dataset_dimension_count())
                self.assertGreaterEqual(ss_sz_max,
                                        current_ss.get_included_dimension_count())
                self.assertLessEqual(ss_sz_min,
                                     current_ss.get_included_dimension_count())
            for j in range(1, len(ss_list1)):
                self.assertFalse(np.array_equal(ss_list1[j].mask, ss_list1[0].mask))


if __name__ == '__main__':
    unittest.main()
