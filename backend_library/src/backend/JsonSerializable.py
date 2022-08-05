import abc


class JsonSerializable(abc.ABC):
    """
    Interface of classes that can be json serialized using to_json
    """

    @abc.abstractmethod
    def to_json(self) -> object:
        """
        Returns a simple object (often a dict) containing all important information about this object
        :return:  an object that can be serialized using json.dump
        """
        pass
