import os
import unittest

from backend.task.TaskHelper import TaskHelper
from backend.DataIO import DataIO


class UnitTestTaskHelper(unittest.TestCase):
    _dir_name: str = os.getcwd()
    _new_dir_path: str = os.path.join(_dir_name, "new_dir")

    _path1: str = os.path.join(_dir_name, "error.csv")
    _path2: str = os.path.join(_dir_name, "error")  # path ends not with .csv
    _path3: str = os.path.join(_dir_name, "empty.csv")
    _error_path1: str = TaskHelper.convert_to_error_csv_path(_path1)
    _error_path2: str = TaskHelper.convert_to_error_csv_path(_path2)
    _error_path3: str = TaskHelper.convert_to_error_csv_path(_path3)

    def setUp(self) -> None:
        self.__clean_created_files_and_directories()

    def tearDown(self):
        self.__clean_created_files_and_directories()

    def __clean_created_files_and_directories(self):
        if os.path.isfile(self._error_path1):
            os.remove(self._error_path1)
        if os.path.isfile(self._error_path2):
            os.remove(self._error_path2)
        if os.path.isfile(self._error_path3):
            os.remove(self._error_path3)

        if os.path.isdir(self._new_dir_path):
            os.rmdir(self._new_dir_path)

    def test_create_error_csv(self):
        error_message: str = "basic error"

        # valid path and message != "" -> everything works
        TaskHelper.save_error_csv(self._path1, error_message)
        self.assertTrue(os.path.isfile(self._error_path1))
        self.assertEqual(error_message, DataIO.read_uncleaned_csv(self._error_path1)[0][0])

        # Not valid path (doesn't end with .csv) -> Raise AssertionError
        with self.assertRaises(AssertionError) as context:
            TaskHelper.save_error_csv(self._path2, error_message)
        self.assertFalse(os.path.isfile(self._error_path2))

        # empty string -> Raise AssertionError
        empty_message: str = ""
        with self.assertRaises(AssertionError) as context:
            TaskHelper.save_error_csv(self._path3, empty_message)
        self.assertFalse(os.path.isfile(self._error_path3))

    def test_convert_to_error_csv_path(self):
        string1: str = ""
        self.assertEqual(".error", TaskHelper.convert_to_error_csv_path(string1))  # add assertion here

        string2: str = "PSE IST DIE BESTE ERFINDUNG DER WELT"
        self.assertEqual("PSE IST DIE BESTE ERFINDUNG DER WELT.error",
                         TaskHelper.convert_to_error_csv_path(string2))  # add assertion here

    def test_create_directory(self):
        TaskHelper.create_directory(self._new_dir_path)
        self.assertTrue(os.path.isdir(self._new_dir_path))

        # Works also when the directory already exists:
        TaskHelper.create_directory(self._new_dir_path)
        self.assertTrue(os.path.isdir(self._new_dir_path))

    def test_iterable_length(self):
        self.assertEqual(0, TaskHelper.iterable_length(iter([])))
        self.assertEqual(4, TaskHelper.iterable_length(iter([1, 2, 531, 412])))
        self.assertEqual(10, TaskHelper.iterable_length(iter([1, 2, 531, 412, -1, 12, 214, 143, 1234, 512])))


if __name__ == '__main__':
    unittest.main()
