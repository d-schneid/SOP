import os
import unittest
import numpy as np

from backend_library.src.main.backend.task.TaskHelper import TaskHelper


class TaskHelperTest(unittest.TestCase):
    dir_name: str = os.getcwd()
    new_dir_path: str = os.path.join(dir_name, "new_dir")

    def tearDown(self):
        if not os.path.isdir(self.new_dir_path):
            os.rmdir(self.new_dir_path)

    def test_convert_to_error_csv_path(self):
        string1: str = ""
        self.assertEqual(".error", TaskHelper.convert_to_error_csv_path(string1))  # add assertion here

        string2: str = "PSE IST DIE BESTE ERFINDUNG DER WELT"
        self.assertEqual("PSE IST DIE BESTE ERFINDUNG DER WELT.error",
                         TaskHelper.convert_to_error_csv_path(string2))  # add assertion here

    def test_is_float_csv(self):
        # Only float32 values -> true
        float32_array: np.ndarray = np.array([127, -128, -127], dtype=np.float32)
        self.assertTrue(TaskHelper.is_float_csv(float32_array))

        # Objects values -> false
        object_array: np.ndarray = np.array([127, -128, -127], dtype=np.object)
        self.assertFalse(TaskHelper.is_float_csv(object_array))

        # Int values -> false
        int_array: np.ndarray = np.array([127, -128, -127], dtype=np.int32)
        self.assertFalse(TaskHelper.is_float_csv(int_array))

        # Empty array
        empty_float32_array: np.ndarray = np.array([], dtype=np.float32)
        self.assertTrue(TaskHelper.is_float_csv(empty_float32_array))

        empty_object_array: np.ndarray = np.array([], dtype=np.object)
        self.assertFalse(TaskHelper.is_float_csv(empty_object_array))

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
