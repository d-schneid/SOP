import os
import unittest
import numpy as np

from backend.task.TaskHelper import TaskHelper


class TaskHelperTest(unittest.TestCase):
    dir_name: str = os.getcwd()
    new_dir_path: str = os.path.join(dir_name, "new_dir")

    def tearDown(self):
        if os.path.isdir(self.new_dir_path):
            os.rmdir(self.new_dir_path)

    def test_convert_to_error_csv_path(self):
        string1: str = ""
        self.assertEqual(".error", TaskHelper.convert_to_error_csv_path(string1))  # add assertion here

        string2: str = "PSE IST DIE BESTE ERFINDUNG DER WELT"
        self.assertEqual("PSE IST DIE BESTE ERFINDUNG DER WELT.error",
                         TaskHelper.convert_to_error_csv_path(string2))  # add assertion here

    def test_create_directory(self):
        TaskHelper.create_directory(self.new_dir_path)
        self.assertTrue(os.path.isdir(self.new_dir_path))

        # Works also when the directory already exists:
        TaskHelper.create_directory(self.new_dir_path)
        self.assertTrue(os.path.isdir(self.new_dir_path))

    def test_iterable_length(self):
        self.assertEqual(0, TaskHelper.iterable_length(iter([])))
        self.assertEqual(4, TaskHelper.iterable_length(iter([1, 2, 531, 412])))
        self.assertEqual(10, TaskHelper.iterable_length(iter([1, 2, 531, 412, -1, 12, 214, 143, 1234, 512])))


if __name__ == '__main__':
    unittest.main()
