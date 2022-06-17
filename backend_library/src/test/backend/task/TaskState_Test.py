import unittest

from backend_library.src.main.backend.task.TaskState import TaskState


class TestTaskState(unittest.TestCase):
    def test_is_finished(self):
        self.assertEqual(TaskState.WAITING.is_finished(), False)
        self.assertEqual(TaskState.RUNNING.is_finished(), False)
        self.assertEqual(TaskState.RUNNING_WITH_ERROR.is_finished(), False)
        self.assertEqual(TaskState.FINISHED.is_finished(), True)
        self.assertEqual(TaskState.FINISHED_WITH_ERROR.is_finished(), True)

    def test_error_occurred(self):
        self.assertEqual(TaskState.WAITING.error_occurred(), False)
        self.assertEqual(TaskState.RUNNING.error_occurred(), False)
        self.assertEqual(TaskState.RUNNING_WITH_ERROR.error_occurred(), True)
        self.assertEqual(TaskState.FINISHED.error_occurred(), False)
        self.assertEqual(TaskState.FINISHED_WITH_ERROR.error_occurred(), True)

if __name__ == '__main__':
    unittest.main()
