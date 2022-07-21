import numpy as np


class ExecutionElementMetricHelper:
    def ComputeOutlierDataPoints(self, execution_element_result_path: str) -> np.ndarray:
        """
        Interprets one result of an ExecutionElement and
        returns an array which says for each data point if it is an outlier or not \n
        :param execution_element_result_path: The execution element result whose outliers should be computed
        :return: An 1D bool array that says for each data point if it is an outlier or not
        """
        pass
