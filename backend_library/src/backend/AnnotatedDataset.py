import numpy as np


class AnnotatedDataset():
    data: np.ndarray
    headers: np.ndarray
    row_mapping: np.ndarray

    def __int__(self, data: np.ndarray, headers: np.ndarray, row_mapping: np.ndarray):
        self.data = data
        self.headers = headers
        self.row_mapping = row_mapping

    def to_single_array(self):
        headers = np.expand_dims(self.headers, 0).astype(object)
        headers_wb = np.concatenate((np.array([[""]]).astype(object), headers), 1)
        rows = np.expand_dims(self.row_mapping.astype(object), 1)
        data = self.data.astype(object)
        rows_data = np.concatenate((rows, data), 1)
        return np.concatenate((headers_wb, rows_data))
