import unittest
from backend.DataIOInputException import DataIOInputException


class UnitTestDataIoInputException(unittest.TestCase):
    def test_dataioinputexception(self):

        # create an DataIoInputException
        my_value_error = ValueError()
        my_message = "this is test message"
        my_exception = DataIOInputException(my_message, my_value_error)

        # assert the correct behaviour
        self.assertEqual(my_exception.exception, my_value_error)
        expected_message_arg = (
            my_message + "; reference error message: " + str(my_value_error)
        )
        self.assertEqual(my_exception.args, (expected_message_arg,))
