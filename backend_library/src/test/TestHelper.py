import shutil
import zipfile


class TestHelper:
    @staticmethod
    def is_same_execution_result_zip(execution_result_zip_path1: str,
                                     execution_result_zip_path2: str):
        is_same_execution_result: bool = False

        # unzip the zip files
        unzipped_path1: str = execution_result_zip_path1
        unzipped_path2: str = execution_result_zip_path2

        # delete unzipped_files
        shutil.rmtree(unzipped_path1)
        shutil.rmtree(unzipped_path2)

        return is_same_execution_result

    @staticmethod
    def __unzip(path_to_zip_file: str, directory_to_extract_to: str):
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)
