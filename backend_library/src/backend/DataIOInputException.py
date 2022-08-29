class DataIOInputException(ValueError):
    """
    Represents an error which can occur when trying to read a dataset from a file.
    """

    def __init__(self, message: str, exception: ValueError) -> None:
        super().__init__(message + "; reference error message: " + str(exception))
        self._exception: ValueError = exception

    @property
    def exception(self) -> ValueError:
        """
        The specific error which occurred
        while trying to read the dataset form a file.
        :return: The specific error which occurred.
        """
        return self._exception
