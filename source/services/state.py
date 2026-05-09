import json
import os

class WorkflowState:
    def __init__(self, log_path="output/audit_log.json"):
        self.log_path = log_path
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_result(self, prompt, explanation, code, result_log, plot_json):
        entry = {
            "prompt": prompt,
            "explanation": explanation,
            "code": code,
            "result_log": result_log,
            "plot_json": plot_json
        }
        self.history.append(entry)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)
        return entry

    def get_history(self):
        return self.history
