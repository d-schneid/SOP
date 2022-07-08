import unittest

from backend.task.TaskState import TaskState


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

    def test_is_running(self):
        self.assertEqual(TaskState.WAITING.is_running(), False)
        self.assertEqual(TaskState.RUNNING.is_running(), True)
        self.assertEqual(TaskState.RUNNING_WITH_ERROR.is_running(), True)
        self.assertEqual(TaskState.FINISHED.is_running(), False)
        self.assertEqual(TaskState.FINISHED_WITH_ERROR.is_running(), False)


if __name__ == '__main__':
    unittest.main()
