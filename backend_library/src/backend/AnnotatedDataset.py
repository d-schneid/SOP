from typing import Optional

import numpy as np


class AnnotatedDataset:
    """
    Represents a dataset with headers and row numbers
    """
    data: np.ndarray
    """the main data of the dataset"""
    headers: np.ndarray
    """Header line of the dataset"""
    row_mapping: np.ndarray
    """An array containing a number for each row in data,
     determining to what original dataset row it belongs"""

    def __init__(self, main_array: np.ndarray, headers: Optional[np.ndarray] = None,
                 row_numbers: Optional[np.ndarray] = None,
                 generate_headers: bool = False, generate_row_numbers: bool = False):
        """
        Creates a new AnnotatedDataset
        :param main_array: the main array, containing the data amongst others
        :param headers: headers to use for the data,
         for behaviour with None see generate_headers
        :param row_numbers: row_numbers to use for the data,
         for behaviour with None see generate_row_numbers
        :param generate_headers: True to generate headers (numbered 1 to n),
         False to read them from the dataset, ignored if headers is not None
        :param generate_row_numbers: True to generate row_numbers (numbered 1 to n),
         False to read them from the dataset, ignored if row_numbers is not None
        """
        assert len(main_array.shape) == 2
        has_row_numbers = row_numbers is None and not generate_row_numbers
        has_header = headers is None and not generate_headers
        no_head = np.delete(main_array, 0, 0) if has_header else main_array
        self.data: np.ndarray = np.delete(no_head, 0, 1) if has_row_numbers else no_head
        if headers is None:
            headers = np.arange(0, self.data.shape[1], 1).astype(np.dtype('<U5'))
        else:
            assert len(headers.shape) == 1,\
                "Header array must have exactly one dimension"
            assert main_array.shape[0] == headers.shape[0],\
                "The size of the header array does not match " \
                "the number of columns of the data"
        if row_numbers is None:
            row_numbers = np.arange(0, self.data.shape[0], 1)
        else:
            assert len(row_numbers.shape) == 1, \
                "Row numbers array must have exactly one dimension"
            assert main_array.shape[1] == row_numbers.shape[0],\
                "The size of the row numbers array does not match " \
                "the number of rows of the data"
        self.headers = main_array[0] if has_header else headers
        self.row_mapping = main_array[:, 0] if has_row_numbers else row_numbers
        if has_row_numbers and has_header:
            self.headers = np.delete(self.headers, 0)
            self.row_mapping = np.delete(self.row_mapping, 0)
        self.row_mapping = self.row_mapping.astype(np.int32)

    def to_single_array(self) -> np.ndarray:
        """Merges the data from this into a single object array,
        may be used for output"""
        headers = np.expand_dims(self.headers, 0).astype(object)
        headers_wb = np.concatenate((np.array([[""]]).astype(object), headers), 1)

        rows = np.expand_dims(self.row_mapping.astype(object), 1)

        data = self.data.astype(object)
        rows_data = np.concatenate((rows, data), 1)

        return np.concatenate((headers_wb, rows_data))
