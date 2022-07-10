class TaskErrorMessages:

    # DatsetCleaning Error messages
    @property
    def cleaning_result_empty(self) -> str:
        return "Error: Cleaning resulted in empty dataset"

    @property
    def cast_to_float32_error(self) -> str:
        return "Error: Cleaning result contained values that were not float32: \n"
