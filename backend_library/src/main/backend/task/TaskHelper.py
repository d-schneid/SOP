import csv
import string
import numpy as np


class TaskHelper:
    @staticmethod
    def save_error_csv(error_file_path: string, error: string) -> None:
        error_message: string = str(error)
        error_csv = open(error_file_path, 'w')
        writer = csv.writer(error_csv)
        writer.writerow(error_message)

    @staticmethod
    def convert_to_error_csv_path(path: string) -> string:
        return path + ".error"  # creates the path for the csv with the error message

    @staticmethod
    def is_float_csv(csv_to_check) -> bool:
        dtype: np.dtype = csv_to_check.dtype
        if dtype == np.float32 or dtype == np.int32:
            return True
        return False
