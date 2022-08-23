import os
import shutil
import zipfile


class TestHelper:
    @staticmethod
    def is_same_execution_result_zip(execution_result_zip_path1: str,
                                     execution_result_zip_path2: str) -> bool:
        is_same_execution_result: bool = False

        # unzip the zip files
        unzipped_path1: str = execution_result_zip_path1 + "_unzipped"
        unzipped_path2: str = execution_result_zip_path2 + "_unzipped"
        TestHelper.__unzip(execution_result_zip_path1, unzipped_path1)
        TestHelper.__unzip(execution_result_zip_path2, unzipped_path2)

        # get all files
        execution1_content: (list[str], list[str]) = TestHelper \
            .__get_files_and_dirs_in_dir(unzipped_path1)
        execution2_content: (list[str], list[str]) = TestHelper \
            .__get_files_and_dirs_in_dir(unzipped_path2)

        # compare files
        if len(execution1_content[0]) != len(execution2_content[0]) or \
                len(execution1_content[1]) != len(execution2_content[1]):
            TestHelper.__cleanup_unzipped_files(unzipped_path1, unzipped_path2)
            return False

        if not TestHelper.__same_list_content(execution1_content[0],
                                              execution2_content[0]) or not \
                TestHelper.__same_list_content(execution1_content[1],
                                               execution2_content[1]):
            TestHelper.__cleanup_unzipped_files(unzipped_path1, unzipped_path2)
            return False

        # delete unzipped_files
        TestHelper.__cleanup_unzipped_files(unzipped_path1, unzipped_path2)

        return True

    @staticmethod
    def __unzip(path_to_zip_file: str, directory_to_extract_to: str):
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)

    @staticmethod
    def __get_files_and_dirs_in_dir(dir_to_inspect: str) -> (list[str], list[str]):
        """
        :param dir_to_inspect: The directory where the file names and dir +
        names are to be outputted
        :return: A tuple of 2 str lists. \n
        The first one contains the file names. \n
        The second one contains the directory names
        """
        file_names: list[str] = list()
        dir_names: list[str] = list()
        for root, dirs, files in os.walk(dir_to_inspect):
            for name in files:
                file_names.append(name)
            for dir_name in dirs:
                dir_names.append(dir_name)

        return file_names, dir_names

    @staticmethod
    def __same_list_content(list1: list[str], list2: list[str]) -> bool:
        assert len(list1) == len(list2)

        list2_copy = list2.copy()  # copy lists to not destroy the original lists

        for element in list1:
            if not list2_copy.remove(element):
                print(element + " is not in list2")  # TODO remove when fixed
                return False  # at least one element from list1 is not in list2
        return True

    @staticmethod
    def __cleanup_unzipped_files(unzipped_path1: str, unzipped_path2):
        shutil.rmtree(unzipped_path1)
        shutil.rmtree(unzipped_path2)
