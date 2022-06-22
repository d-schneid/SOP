import csv
import string


class TaskHelper:
    def save_error_csv(self, error_file_path: string, error: string):
        error_message: string = str(error)
        error_csv = open(error_file_path, 'w')
        writer = csv.writer(error_csv)
        writer.writerow(error_message)
