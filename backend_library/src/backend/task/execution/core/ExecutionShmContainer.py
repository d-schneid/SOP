import multiprocessing
from multiprocessing import shared_memory
from multiprocessing.shared_memory import SharedMemory
from typing import Optional

import numpy as np

from backend.AnnotatedDataset import AnnotatedDataset


class ExecutionShmContainer:
    """Manages the shared memory of an execution"""
    # shared memory
    _shared_memory_name: Optional[str] = None
    _shared_memory_on_main: Optional[SharedMemory] = None
    _dataset_on_main: Optional[np.ndarray] = None

    _rownrs_shm_name: Optional[str] = None
    _rownrs_shm_on_main: Optional[SharedMemory] = None
    _rownrs_on_main: Optional[np.ndarray] = None

    def make_shms(self, datapoint_count: int, ds_dim_count: int):
        """Creates the shared memory objects"""
        entry_count = datapoint_count * ds_dim_count
        dtype = np.dtype('f4')
        size = entry_count * dtype.itemsize
        self._shared_memory_on_main = SharedMemory(None, True, size)
        self._shared_memory_name = self._shared_memory_on_main.name
        self._dataset_on_main = np.ndarray((datapoint_count, ds_dim_count),
                                           buffer=self._shared_memory_on_main.buf,
                                           dtype=dtype)
        self._rownrs_shm_on_main = SharedMemory(None, True, datapoint_count * 4)
        self._rownrs_shm_name = self._rownrs_shm_on_main.name
        self._rownrs_on_main = np.ndarray([datapoint_count],
                                          buffer=self._rownrs_shm_on_main.buf,
                                          dtype=np.int32)

    def copy_rns_back(self) -> np.ndarray:
        """Copies the row numbers out of the shared memory and returns it"""
        result = np.copy(self._rownrs_on_main)
        self.unload_rownrs()
        return result

    def unload_rownrs(self):
        if self._rownrs_shm_name is not None:
            self._rownrs_shm_on_main.close()
            self._rownrs_shm_on_main.unlink()
            self._rownrs_shm_name = None
            self._rownrs_on_main = None
            self._rownrs_shm_on_main = None

    def unload_dataset(self, ignore_if_done: bool = False) -> None:
        """
        Unloads the cleaned dataset from shared_memory. \n
        :return: None
        """
        assert ignore_if_done or self._shared_memory_name is not None, \
            "If there is no shared memory currently loaded it can not be unloaded"
        if self._shared_memory_name is not None:
            self._shared_memory_on_main.unlink()
            self._shared_memory_on_main.close()
            self._shared_memory_name = None
        self.unload_rownrs()

    def store_dataset(self, dataset: AnnotatedDataset):
        """Stores a dataset in the shared memory"""
        shm = shared_memory.SharedMemory(self._shared_memory_name, False)
        ndarray = np.ndarray(dataset.data.shape, dataset.data.dtype, shm.buf)
        shared_data = ndarray
        rownrs_shm = shared_memory.SharedMemory(self._rownrs_shm_name, False)
        rownrs_shared_data = np.ndarray([dataset.data.shape[0]], np.int32,
                                        rownrs_shm.buf)
        shared_data[:] = dataset.data[:]
        rownrs_shared_data[:] = dataset.row_mapping[:]
        if type(multiprocessing.current_process()) == multiprocessing.Process:
            shm.close()
            rownrs_shm.close()

    @property
    def shared_memory_name(self) -> Optional[str]:
        """Name of the shm containing the datasets data section"""
        return self._shared_memory_name

    @property
    def dataset_on_main(self) -> Optional[np.ndarray]:
        """Returns an np.array of the dataset,
         the contents of which are not usable outside the main process"""
        return self._dataset_on_main
