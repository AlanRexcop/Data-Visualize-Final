import unittest
import os
import json
from source.services.state import WorkflowState

class TestWorkflowState(unittest.TestCase):
    def setUp(self):
        self.test_log = "test_audit.json"
        self.state = WorkflowState(log_path=self.test_log)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def test_save_and_retrieve_result(self):
        self.state.save_result("test prompt", "test explanation", "print('hello')", "log output", "{}")
        history = self.state.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['prompt'], "test prompt")

if __name__ == '__main__':
    unittest.main()
