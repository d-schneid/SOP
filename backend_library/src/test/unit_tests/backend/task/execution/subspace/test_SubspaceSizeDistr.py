import unittest
import numpy as np

from backend.task.execution.subspace.UniformSubspaceDistribution import \
    UniformSubspaceDistribution


class UnitTestSubspaceSizeDistr(unittest.TestCase):
    uni_distr_para = [
        (1, 1, 1, 1, 1, 1),
        (3, 2, 1, 2, 1, 2),
        (3, 2, 1, 2, 2, 1),
        (1, 2, 1, 2, 2, 0)]

    def test_uniform_distr(self):
        for ss_count, ds_size, min_s, max_s, check_s, exp_count in self.uni_distr_para:
            uni_dist = UniformSubspaceDistribution(min_s, max_s)
            ss_sizes = uni_dist.get_subspace_counts(ss_count, ds_size)
            self.assertEqual(exp_count, ss_sizes[check_s])
            self.assertEqual(ss_count, sum(ss_sizes.values()))
            for k, v in ss_sizes.items():
                self.assertLessEqual(min_s, k)
                self.assertGreaterEqual(max_s, k)
                self.assertGreaterEqual(v, 0)

    enough_ss_para = [
        (1, 1, 1, 1, True),
        (2, 1, 1, 1, False),
        (20, 5, 2, 3, True),
        (21, 5, 2, 3, False),
        (12, 4, 1, 3, True),
        (13, 4, 1, 3, False),
        (7, 4, 1, 4, True),
        (8, 4, 1, 4, False)
    ]

    def test_enough_ss(self):
        for ss_count, ds_size, min_s, max_s, enough_ss_exp in self.enough_ss_para:
            uni_dist = UniformSubspaceDistribution(min_s, max_s)
            has_enough_ss = uni_dist.has_enough_subspaces(ss_count, ds_size)
            self.assertEqual(enough_ss_exp, has_enough_ss)


if __name__ == '__main__':
    unittest.main()
