import os
import shutil
import unittest
import zipfile
from typing import List

from backend.task.TaskHelper import TaskHelper
from backend.DataIO import DataIO


class UnitTestTaskHelper(unittest.TestCase):
    _dir_name: str = os.getcwd()
    _test_dir_path: str = os.path.join(_dir_name, "new_dir")

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
        if os.path.isdir(self._test_dir_path):
            shutil.rmtree(self._test_dir_path)

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
        strings: List[str] = ["", "PSE IST DIE BESTE ERFINDUNG DER WELT", "...hier ist ein komischer string?!?..."]

        for string in strings:
            self.assertEqual(string + ".error", TaskHelper.convert_to_error_csv_path(string))

    def test_create_directory(self):
        TaskHelper.create_directory(self._test_dir_path)
        self.assertTrue(os.path.isdir(self._test_dir_path))

        # Works also when the directory already exists:
        TaskHelper.create_directory(self._test_dir_path)
        self.assertTrue(os.path.isdir(self._test_dir_path))

    def test_iterable_length(self):
        self.assertEqual(0, TaskHelper.iterable_length(iter([])))
        self.assertEqual(4, TaskHelper.iterable_length(iter([1, 2, 531, 412])))
        self.assertEqual(10, TaskHelper.iterable_length(iter([1, 2, 531, 412, -1, 12, 214, 143, 1234, 512])))

    # ---- Tests for zip_dir ----

    def test_zip_dir_correct(self):
        # first, create a directory with files to zip
        zip_test_dir: str = os.path.join(self._test_dir_path, "test_zip_dir")

        UnitTestTaskHelper._create_dirs_and_text_files(zip_test_dir,
            [["dir_01", "baum.txt", "Hier steht ein Baum."],
             ["dir_01/sub_dir", "me.mo", "Wer das liest ist doof."],
             ["dir_03/sub_dir_01/sub_sub_dir", "motto", "War is peace. Freedom is slavery. Ignorance is strength."]])

        # then, zip the directory
        zip_file: str = os.path.join(self._test_dir_path, "test_zip_01.zip")

        #  check if the zipping was successful
        TaskHelper.zip_dir(zip_test_dir, zip_file)
        self.assertTrue(UnitTestTaskHelper._check_zip_identical(zip_file, zip_test_dir))

    # ---- static helper methods ---

    @staticmethod
    def _check_zip_identical(zip_file: str, org_dir_path: str) -> bool:

        # compare every file in the zip-file with the given directory
        with zipfile.ZipFile(zip_file, "r") as zfh:
            for file in zfh.infolist():
                org_file: str = os.path.join(org_dir_path, "..", file.filename)

                # check if the file exists in the original dir
                if not os.path.isfile(org_file):
                    return False

                # compare the contents
                with open(org_file) as org_content:
                    if zfh.read(file).decode("utf-8") != org_content.read():
                        return False

                # if all matches, delete the original file
                os.remove(org_file)



        """# compare every file in the extracted directory
        unzip_dir_path: str = zip_file + "_extract/"
        for root, dirs, files in os.walk(unzip_dir_path):
            for file in files:
                extracted_file: str = os.path.join(root, file)
                rel_file_path: str = os.path.relpath(extracted_file, unzip_dir_path)
                original_file: str = os.path.join(org_dir_path, "..", rel_file_path)  # TODO

                if os.path.isfile(original_file):
                    if UnitTestTaskHelper._check_same_file_content(extracted_file, original_file):
                        os.remove(extracted_file)
                        os.remove(original_file)
                    else:
                        return False"""

        # check, if there are files in the original directory left --> they have not been zipped
        for root, dirs, files in os.walk(org_dir_path):
            for file in files:
                if os.path.isfile(os.path.join(root, file)):
                    return False

        # otherwise, every file was zipped and had the correct content
        return True

    @staticmethod
    def _create_dirs_and_text_files(abs_path: str, content: List[List[str]]):
        for dir_name, file_name, file_content in content:
            # print (dir_name, file_name, file_content)

            abs_dir: str = os.path.join(abs_path, dir_name)

            os.makedirs(abs_dir)
            with open(os.path.join(abs_dir, file_name), "w") as fh:
                fh.write(file_content)


if __name__ == '__main__':
    unittest.main()