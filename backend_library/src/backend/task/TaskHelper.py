import os
import random
import shutil
import string
import zipfile
import zlib

import numpy as np
from collections.abc import Iterable
from backend.DataIO import DataIO


class TaskHelper:
    """
    Static helping methods for the subclasses of Task.
    """
    @staticmethod
    def save_error_csv(path: str, error_message: str) -> None:
        """ Converts path into the error_file_path and saves the error-csv-file there.
        :param path: The absolute path where the csv will be stored (contains the name of the csv and ends with .csv).
        :param error_message: The error message that will be written into the error_csv file.
        It has to be not equal to ""
        :return: None
        """
        assert path.endswith(".csv")
        assert error_message != ""

        error_file_path: str = TaskHelper.convert_to_error_csv_path(path)
        error_message: str = error_message

        to_save: np.ndarray = np.asarray([error_message], object)
        DataIO.write_csv(error_file_path, to_save)

    @staticmethod
    def convert_to_error_csv_path(path: str) -> str:
        """ Converts the path to the path where the error_csv will be stored.
        :param path: The absolute path that will be converted.
        :return: The converted path into the error_csv path.
        """
        return path + ".error"

    @staticmethod
    def create_directory(path: str) -> None:
        """
        :param path: The absolute path where the new directory will be created
        :return: None
        """
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def iterable_length(iterable: Iterable) -> int:
        """
        :param iterable: The iterable whose length is requested
        :return: Returns the length of the iterable.
        """
        return sum(1 for e in iterable)

    @staticmethod
    def zip_dir(dir_path: str, zip_path: str, compression_level: int = zlib.Z_DEFAULT_COMPRESSION) -> None:
        """
        Zips the specified directory and saves the created zip-file at the specified location.

        No files are deleted. The files are compressed when added to the zip archive (with the zlib module).
        A ".temp" suffix is appended at the end of the file that is removed when the complete
        zipping process has finished, so that in case of e.g. a server crash a corrupted file can be spotted.
        If the ZIP-file is larger than 4 GiB, than a ZIP-file with the ZIP64 extension is created automatically.

        Errors due to missing read / write permissions and missing libraries (zlib) are not caught.

        :param dir_path: The path of the dir to zip. The directory must exist.
        :param zip_path: The path to store the created zip-file at. The file must not exist.
        :param compression_level: The level of compression. Values from 0 to 9 are accepted.
                            Standard is the standard value of the zlib module, which offers a compromise in
                            speed and compression.
        """
        assert (0 <= compression_level <= 9) or (compression_level == zlib.Z_DEFAULT_COMPRESSION)
        assert not os.path.isfile(zip_path)
        assert os.path.isdir(dir_path)

        temp_zip_path: str = zip_path + ".temp"  # temporary file path, with ".temp" suffix

        # use package os, as shutil.make_archive() is not thread-safe
        zipfile_handle: zipfile.ZipFile = zipfile.ZipFile(temp_zip_path, mode="x",
                                                          compression=zipfile.ZIP_DEFLATED,
                                                          allowZip64=True,
                                                          compresslevel=compression_level)

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                zipfile_handle.write(os.path.join(root, file),
                                     os.path.relpath(os.path.join(root, file),
                                                     os.path.join(dir_path, '..')))

        zipfile_handle.close()

        os.rename(temp_zip_path, zip_path)  # is a atomic operation (POSIX requirement)

    @staticmethod
    def del_dir(dir_path: str):
        """
        Deletes the given directory, including all containing files and subdirectories.

        Errors due to missing read / write permissions (e.g. when attempting to
        delete read-only files) are not caught.

        :param dir_path: The directory to be deleted (recursively). Must not be a single file.
        """
        assert os.path.isdir(dir_path)

        shutil.rmtree(dir_path)

    @staticmethod
    def shm_name_generator():
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(40))
