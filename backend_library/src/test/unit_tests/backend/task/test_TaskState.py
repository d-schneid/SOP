import unittest

from backend.task.TaskState import TaskState


class UnitTestTaskState(unittest.TestCase):
    def test_is_finished(self):
        self.assertFalse(TaskState.WAITING.is_finished())
        self.assertFalse(TaskState.RUNNING.is_finished())
        self.assertFalse(TaskState.RUNNING_WITH_ERROR.is_finished())
        self.assertTrue(TaskState.FINISHED.is_finished())
        self.assertTrue(TaskState.FINISHED_WITH_ERROR.is_finished())

    def test_error_occurred(self):
        self.assertFalse(TaskState.WAITING.error_occurred())
        self.assertFalse(TaskState.RUNNING.error_occurred())
        self.assertTrue(TaskState.RUNNING_WITH_ERROR.error_occurred())
        self.assertFalse(TaskState.FINISHED.error_occurred())
        self.assertTrue(TaskState.FINISHED_WITH_ERROR.error_occurred())

    def test_is_running(self):
        self.assertFalse(TaskState.WAITING.is_running())
        self.assertTrue(TaskState.RUNNING.is_running())
        self.assertTrue(TaskState.RUNNING_WITH_ERROR.is_running())
        self.assertFalse(TaskState.FINISHED.is_running())
        self.assertFalse(TaskState.FINISHED_WITH_ERROR.is_running())


if __name__ == '__main__':
    unittest.main()
