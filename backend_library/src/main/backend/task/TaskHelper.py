import csv
import string
import numpy as np


class TaskHelper:
    @staticmethod
    #Converts file_path into the error_file_path and saves the error-csv-file there.
    def save_error_csv(file_path: string, error_message: string) -> None:
        error_file_path: string = TaskHelper.convert_to_error_csv_path(file_path)
        error_message: string = error_message
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
