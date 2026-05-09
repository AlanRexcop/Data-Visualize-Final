import unittest
from unittest.mock import MagicMock
from source.services.ai_logic import get_ai_analysis

class TestAgentIntegration(unittest.TestCase):
    def test_get_ai_analysis_returns_json(self):
        # Mocking genai client call inside ai_logic
        api_key = "AIzaSyBrM4LUcpkPpgDWCFvXEWi1hplRs6utU3U"
        prompt = "plot biểu đồ biến đọc giá theo tháng, tổng hợp các tháng của các năm để thấy xu hướng chung của các tháng"
        
        # We perform an end-to-end test using the tracer bullet
        result = get_ai_analysis(api_key, prompt)
        
        self.assertIn('explanation', result)
        self.assertIn('code', result)
        self.assertTrue(len(result['code']) > 0)

if __name__ == '__main__':
    unittest.main()
