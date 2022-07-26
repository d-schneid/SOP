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
        os.makedirs(self._test_dir_path)

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
        self.assertEqual(error_message, DataIO.read_uncleaned_csv(self._error_path1, has_header=None)[0][0])

        # Not valid path (doesn't end with .csv) -> Raise AssertionError
        with self.assertRaises(AssertionError):
            TaskHelper.save_error_csv(self._path2, error_message)
        self.assertFalse(os.path.isfile(self._error_path2))

        # empty string -> Raise AssertionError
        empty_message: str = ""
        with self.assertRaises(AssertionError):
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
        zip_test_dir: str = os.path.join(self._test_dir_path, "test_zip_dir_correct")

        UnitTestTaskHelper._create_dirs_and_text_files(zip_test_dir,
                                                       [["dir_01", "baum.txt", "Hier steht ein Baum."],
                                                        ["dir_01/sub_dir", "me.mo", "Wer das liest ist doof."],
                                                        ["dir_03/sub_dir_01/sub_sub_dir", "motto",
                                                         "War is peace. Freedom is slavery. Ignorance is strength."]])

        # then, zip the directory
        zip_file_running: str = os.path.join(self._test_dir_path, "test_zip_01_running.zip")
        zip_file_final: str = os.path.join(self._test_dir_path, "test_zip_01_final.zip")

        #  check if the zipping was successful
        TaskHelper.zip_dir(zip_path_running=zip_file_running, zip_path_final=zip_file_final, dir_path=zip_test_dir)
        self.assertTrue(UnitTestTaskHelper._check_zip_identical(zip_file_final, zip_test_dir))

    def test_zip_bad_params(self):
        # first, create a path to a non-existing directory and write a file
        dir_missing: str = os.path.join(self._test_dir_path, "test_zip_bad_params__missing")

        dir_existing: str = os.path.join(self._test_dir_path, "test_zip_bad_params__existing")
        UnitTestTaskHelper._create_dirs_and_text_files(dir_existing,
                                                       [["dir_01", "baum.txt", "Hier steht ein Baum."],
                                                        ["dir_01/sub_dir", "me.mo", "Wer das liest ist doof."],
                                                        ["dir_03/sub_dir_01/sub_sub_dir", "motto",
                                                         "War is peace. Freedom is slavery. Ignorance is strength."]])

        file_existing: str = os.path.join(self._test_dir_path, "existing_file.txt")
        with open(file_existing, "w") as file:
            file.write("Diese Datei existiert schon!")
        file_missing_form: str = os.path.join(self._test_dir_path, "non-existing-file{count}.txt")

        # try to zip with bad parameters
        for dir_path, zip_path_running, zip_path_final, compression_level, f_run_exist, f_final_exist in [
            [dir_missing, file_missing_form.format(count=0), file_missing_form.format(count=1), 5, False, False],
            [dir_existing, file_existing, file_missing_form.format(count=2), 5, True, False],
            [dir_existing, file_missing_form.format(count=3), file_existing, 68, False, True],
            [dir_existing, file_missing_form.format(count=4), file_missing_form.format(count=5), 100, False, False],
            [dir_missing, file_existing, file_missing_form.format(count=6), 200, True, False]]:

            with self.assertRaises(AssertionError):
                TaskHelper.zip_dir(dir_path=dir_path, zip_path_running=zip_path_running,
                                   zip_path_final=zip_path_final, compression_level=compression_level)

            if not f_run_exist:
                self.assertFalse(os.path.isfile(zip_path_running))
            if not f_final_exist:
                self.assertFalse(os.path.isfile(zip_path_final))

    # ---- tests for del_dir ----

    def test_del_dir_correct(self):
        # first, create a directory to delete
        test_del_dir: str = os.path.join(self._test_dir_path, "test_del_dir_correct")

        UnitTestTaskHelper._create_dirs_and_text_files(test_del_dir,
                                                       [["dir_01", "baum.txt", "Hier steht ein Baum."],
                                                        ["dir_01/sub_dir", "me.mo", "Wer das liest ist doof."],
                                                        ["dir_03/sub_dir_01/sub_sub_dir", "motto",
                                                         "War is peace. Freedom is slavery. Ignorance is strength."]])

        TaskHelper.del_dir(test_del_dir)
        self.assertFalse(os.path.isdir(test_del_dir))

    def test_del_dir_bad_params(self):
        dir_non_existing: str = os.path.join(self._test_dir_path, "test_del_dir_missing")

        with self.assertRaises(AssertionError):
            TaskHelper.del_dir(dir_non_existing)

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
            abs_dir: str = os.path.join(abs_path, dir_name)

            os.makedirs(abs_dir)
            with open(os.path.join(abs_dir, file_name), "w") as fh:
                fh.write(file_content)


if __name__ == '__main__':
    unittest.main()
