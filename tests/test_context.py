import unittest
import os
from source.services.state import WorkflowState
from source.services.ai_logic import get_ai_analysis

class TestContextAwarePrompting(unittest.TestCase):
    def test_inject_context(self):
        state = WorkflowState(log_path="test_context.json")
        # Save a dummy result
        state.save_result("previous prompt", "explanation", "code", "log", "{}")
        
        previous_result = state.get_result(0)
        context = f"Prompt: {previous_result['prompt']}\nExplanation: {previous_result['explanation']}"
        
        # Verify injection
        api_key = "AIzaSyBrM4LUcpkPpgDWCFvXEWi1hplRs6utU3U"
        prompt = "Analyze based on previous context"
        
        # Run test
        result = get_ai_analysis(api_key, prompt, context=context)
        self.assertIn('explanation', result)

    def tearDown(self):
        if os.path.exists("test_context.json"):
            os.remove("test_context.json")

if __name__ == '__main__':
    unittest.main()
