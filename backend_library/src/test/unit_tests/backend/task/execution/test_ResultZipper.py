import os
import shutil
import unittest
import zipfile
from typing import List, Callable

from backend.task.execution import ResultZipper
from backend.task import TaskState


class UnitTestResultZipper(unittest.TestCase):
    _test_dir_path: str = os.path.join(os.getcwd(), "UnitTestResultZipper_TestDir")
    _callback_file_path: str = os.path.join(_test_dir_path, "callback_file.txt")
    _some_dir_structure = [
        ["dir_01", "baum.txt", "Hier steht ein Baum."],
        ["dir_01/sub_dir", "me.mo", "Wer das liest ist doof."],
        [
            "dir_03/sub_dir_01/sub_sub_dir",
            "motto",
            "War is peace. Freedom is slavery. Ignorance is strength.",
        ],
    ]

    def setUp(self) -> None:
        UnitTestResultZipper._clean_dir(UnitTestResultZipper._test_dir_path)
        os.makedirs(UnitTestResultZipper._test_dir_path)

    def tearDown(self) -> None:
        UnitTestResultZipper._clean_dir(UnitTestResultZipper._test_dir_path)

    def test_correct_no_error(self):
        self._test_with_good_args(
            user_id=5,
            task_id=2,
            error_occurred=False,
            callback=UnitTestResultZipper._test_callback,
            dir_path="some_dir",
            dir_struct=UnitTestResultZipper._some_dir_structure,
            zip_file_temp="temp",
            zip_file_final="final",
        )

    def test_good_args_with_error(self):
        self._test_with_good_args(
            user_id=10,
            task_id=3,
            error_occurred=True,
            callback=UnitTestResultZipper._test_callback,
            dir_path="test_with_err",
            dir_struct=UnitTestResultZipper._some_dir_structure,
            zip_file_temp="temp_zip.zip",
            zip_file_final="final_zip.zip"
        )

    def test_good_args_file_existing(self):

        # create existing files and fill them with content
        file_name_1 = "i_am_existing.zip"
        file_content_1 = "this is file 1"
        file_name_2 = "i_exist_also.zip"
        file_content_2 = "this is file number 2"

        file_path_1 = os.path.join(UnitTestResultZipper._test_dir_path, file_name_1)
        file_path_2 = os.path.join(UnitTestResultZipper._test_dir_path, file_name_2)

        file_list = [[file_path_1, file_content_1], [file_path_2, file_content_2]]

        for file_name, file_content in file_list:
            with open(file_name, "w") as file:
                file.write(file_content)

        self._test_with_good_args(
            user_id=550,
            task_id=6554654,
            error_occurred=False,
            callback=UnitTestResultZipper._test_callback,
            dir_path="lalala",
            dir_struct=UnitTestResultZipper._some_dir_structure,
            zip_file_temp=file_name_1,
            zip_file_final=file_name_2,
        )

        # check, that the files have been overwritten / deleted
        # (e.g. the contents are not the old ones)

        # temp file should be deleted after overwriting
        self.assertFalse(os.path.isfile(file_path_1))

        # final file should have been overwritten and be zip file
        self.assertTrue(zipfile.is_zipfile(file_path_2))

    def test_bad_args(self):
        dir_missing: str = os.path.join(
            UnitTestResultZipper._test_dir_path, "dir-not-existing"
        )
        dir_existing: str = os.path.join(
            UnitTestResultZipper._test_dir_path, "dir-is-existing"
        )
        UnitTestResultZipper._create_dirs_and_text_files(
            dir_existing,
            self._some_dir_structure,
        )

        file_missing_form: str = os.path.join(
            UnitTestResultZipper._test_dir_path, "file-not-existing{count}.zip"
        )
        file_existing: str = os.path.join(
            UnitTestResultZipper._test_dir_path, "file-is-existing.zip"
        )
        with open(file_existing, "w") as file:
            file.write("Diese Datei existiert.")

        for (
                user_id,
                task_id,
                error_occured,
                callback,
                dir_path,
                zip_path_temp,
                zip_path_final,
                f_temp_exist,
                f_final_exist,
        ) in [
            [
                -5,
                2,
                True,
                UnitTestResultZipper._test_callback,
                dir_existing,
                file_missing_form.format(count=0),
                file_missing_form.format(count=1),
                False,
                False,
            ],
            [
                5,
                -3,
                False,
                UnitTestResultZipper._test_callback,
                dir_existing,
                file_missing_form.format(count=2),
                file_missing_form.format(count=3),
                False,
                False,
            ],
            [
                5,
                3,
                True,
                UnitTestResultZipper._test_callback,
                dir_missing,
                file_missing_form.format(count=4),
                file_missing_form.format(count=5),
                False,
                False,
            ],
            [
                5,
                3,
                False,
                UnitTestResultZipper._test_callback,
                dir_missing,
                file_existing,
                file_existing,
                True,
                True,
            ],
            [
                -5,
                -15,
                True,
                UnitTestResultZipper._test_callback,
                dir_missing,
                file_existing,
                file_missing_form.format(count=6),
                True,
                False,
            ],
        ]:

            with self.assertRaises(AssertionError):
                ResultZipper.ResultZipper(
                    user_id,
                    task_id,
                    error_occured,
                    callback,
                    dir_path,
                    zip_path_temp,
                    zip_path_final,
                )

            if not f_final_exist:
                self.assertFalse(os.path.isfile(zip_path_final))

    # ---- non-static helper methods ----
    def _test_with_good_args(
            self,
            user_id: int,
            task_id: int,
            error_occurred: bool,
            callback: Callable,
            dir_path: str,
            dir_struct: List[List[str]],
            zip_file_temp: str,
            zip_file_final: str,
    ):

        dir_path: str = os.path.join(
            UnitTestResultZipper._test_dir_path, dir_path
        )
        UnitTestResultZipper._create_dirs_and_text_files(
            dir_path,
            dir_struct,
        )

        zip_path_temp: str = os.path.join(
            UnitTestResultZipper._test_dir_path, zip_file_temp
        )
        zip_path_final: str = os.path.join(
            UnitTestResultZipper._test_dir_path, zip_file_final
        )

        result_zipper = ResultZipper.ResultZipper(
            user_id,
            task_id,
            error_occurred,
            callback,
            dir_path,
            zip_path_temp,
            zip_path_final,
        )

        # check the properties
        self.assertEqual(result_zipper.task_id, task_id)
        self.assertEqual(result_zipper.user_id, user_id)
        self.assertEqual(result_zipper.priority, 50)

        # call the do_work method
        result_zipper.do_work()

        # check, if a zip-file was created and the directory deleted
        self.assertTrue(os.path.isfile(zip_path_final))
        self.assertFalse(os.path.isdir(dir_path))

        # check, if the callback-function worked
        if error_occurred:
            expected_task_state = TaskState.TaskState.FINISHED_WITH_ERROR
        else:
            expected_task_state = TaskState.TaskState.FINISHED

        with open(UnitTestResultZipper._callback_file_path) as file:
            self.assertEqual(
                file.read(), str([task_id, expected_task_state, 1])
            )

    # ---- static helper methods ----

    @staticmethod
    def _clean_dir(path: str):
        if os.path.isdir(path):
            shutil.rmtree(path)

    @staticmethod
    def _test_callback(task_id: int, task_state: TaskState, progress: float) -> None:
        with open(UnitTestResultZipper._callback_file_path, "w") as file:
            file.write(str([task_id, task_state, progress]))

    @staticmethod
    def _create_dirs_and_text_files(abs_path: str, content: list[list[str]]):
        for dir_name, file_name, file_content in content:
            abs_dir: str = os.path.join(abs_path, dir_name)

            os.makedirs(abs_dir)
            with open(os.path.join(abs_dir, file_name), "w") as fh:
                fh.write(file_content)


if __name__ == "__main__":
    unittest.main()
