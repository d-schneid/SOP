import unittest

from backend.task.TaskErrorMessages import TaskErrorMessages


class MyTestCase(unittest.TestCase):

    _taskErrorMessages: TaskErrorMessages = TaskErrorMessages()

    def test_cleaning_result_empty(self):
        self.assertEqual("Error: Cleaning resulted in empty dataset",
                         self._taskErrorMessages.cleaning_result_empty)

    def test_cast_to_float32_error(self):
        self.assertEqual("Error: Cleaning result contained values "
                         "that were not float32: \n",
                         self._taskErrorMessages.cast_to_float32_error)


if __name__ == '__main__':
    unittest.main()
