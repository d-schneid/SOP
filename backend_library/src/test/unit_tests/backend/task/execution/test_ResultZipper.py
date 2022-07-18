import os
import shutil
import unittest
from typing import List

from backend.task.execution import ResultZipper
from backend.task import TaskState


class UnitTestResultZipper(unittest.TestCase):
    _test_dir_path: str = os.path.join(os.getcwd(), "UnitTestResultZipper_TestDir")
    _callback_file_path: str = os.path.join(_test_dir_path, "callback_file.txt")

    def setUp(self) -> None:
        UnitTestResultZipper._clean_dir(UnitTestResultZipper._test_dir_path)
        os.makedirs(UnitTestResultZipper._test_dir_path)

    def tearDown(self) -> None:
        UnitTestResultZipper._clean_dir(UnitTestResultZipper._test_dir_path)

    def test_correct(self):
        # create a ResultZipper object
        user_id: int = 5
        task_id: int = 2
        error_occurred: bool = False

        dir_path: str = os.path.join(UnitTestResultZipper._test_dir_path, "test_correct")
        UnitTestResultZipper._create_dirs_and_text_files(dir_path,
                                                       [["dir_01", "baum.txt", "Hier steht ein Baum."],
                                                        ["dir_01/sub_dir", "me.mo", "Wer das liest ist doof."],
                                                        ["dir_03/sub_dir_01/sub_sub_dir", "motto",
                                                         "War is peace. Freedom is slavery. Ignorance is strength."]])

        zip_path: str = os.path.join(UnitTestResultZipper._test_dir_path, "test_correct_non_exst_file")

        result_zipper = ResultZipper.ResultZipper(user_id, task_id, error_occurred,
                                                  UnitTestResultZipper._test_callback, dir_path, zip_path)

        # check the properties
        self.assertEqual(result_zipper.task_id, task_id)
        self.assertEqual(result_zipper.user_id, user_id)

        # call the do_work method
        result_zipper.do_work()

        # check, if a zip-file was created and the directory deleted
        self.assertTrue(os.path.isfile(zip_path))
        self.assertFalse(os.path.isdir(dir_path))

        # check, if the callback-function worked
        with open(UnitTestResultZipper._callback_file_path) as file:
            self.assertTrue(file.read() == str([task_id, TaskState.TaskState.FINISHED, 1]))


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
    def _create_dirs_and_text_files(abs_path: str, content: List[List[str]]):
        for dir_name, file_name, file_content in content:
            abs_dir: str = os.path.join(abs_path, dir_name)

            os.makedirs(abs_dir)
            with open(os.path.join(abs_dir, file_name), "w") as fh:
                fh.write(file_content)

if __name__ == '__main__':
    unittest.main()
