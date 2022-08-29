import os
import shutil
import zipfile
import zlib

import numpy as np

from backend.DataIO import DataIO


class TaskHelper:
    """
    Static helping methods for the subclasses of Task.
    """
    @staticmethod
    def save_error_csv(path: str, error_message: str) -> None:
        """ Converts path into the error_file_path and saves the error-csv-file there.
        :param path: The absolute path where the csv will be stored
        (contains the name of the csv and ends with .csv).
        :param error_message: The error message that will
        be written into the error_csv file.
        It has to be not equal to ""
        :return: None
        """
        assert path.endswith(".csv")
        assert error_message != ""

        error_file_path: str = TaskHelper.convert_to_error_csv_path(path)

        to_save: np.ndarray = np.asarray([[error_message]], str)
        DataIO.save_write_csv(error_file_path + ".running", error_file_path, to_save)

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
    def zip_dir(dir_path: str, zip_path_running: str, zip_path_final: str,
                compression_level: int = zlib.Z_DEFAULT_COMPRESSION) -> None:
        """
        Zips the specified directory and saves the created zip-file
        at the specified (final) location.

        During creation-time, the zip-file will be stored at the path zip_path_running,
        and moved to the path zip_path_final after the creation has finished.
        This is to ensure that a corrupted
        file can be spotted, e.g. after a server crash. For this to work,
        both paths have to be located in the same file system.
        No files are deleted. The files are compressed when added to the zip archive
        (with the zlib module).
        If the ZIP-file is larger than 4 GiB,
        than a ZIP-file with the ZIP64 extension is created automatically.

        Errors due to missing read / write permissions
        and missing libraries (zlib) are not caught.

        :param dir_path: The path of the directory to zip. The directory must exist.
        :param zip_path_running: The path to store the created zip-file
        at creation time. The file must not exist.
        Should be on same file system as zip_path_final.
        :param zip_path_final: The path to store the created zip-file
        after the creation. The file must not exist.
        Should be on same file system as zip_path_running.
        :param compression_level: The level of compression.
        Values from 0 to 9 are accepted.
        Standard is the standard value of the zlib module, which offers a compromise in
        speed and compression.
        """
        assert (0 <= compression_level <= 9) or (
            compression_level == zlib.Z_DEFAULT_COMPRESSION)
        assert not os.path.isfile(zip_path_running)
        assert not os.path.isfile(zip_path_final)
        assert os.path.isdir(dir_path)

        # use package os, as shutil.make_archive() is not thread-safe
        zipfile_handle: zipfile.ZipFile = zipfile.ZipFile(
            zip_path_running, mode="x", compression=zipfile.ZIP_DEFLATED,
            allowZip64=True, compresslevel=compression_level)

        # add all files
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                zipfile_handle.write(os.path.join(root, file),
                                     os.path.relpath(os.path.join(root, file),
                                                     os.path.join(dir_path, '..')))

        zipfile_handle.close()

        # is an atomic operation, *if* both paths are on the same file system
        shutil.move(zip_path_running, zip_path_final)

    @staticmethod
    def del_dir(dir_path: str):
        """
        Deletes the given directory, including all containing files and subdirectories.

        Errors due to missing read / write permissions (e.g. when attempting to
        delete read-only files) are not caught.

        :param dir_path: The directory to be deleted (recursively).
        Must not be a single file.
        """
        assert os.path.isdir(dir_path)

        shutil.rmtree(dir_path)
