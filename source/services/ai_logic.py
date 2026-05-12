# source/services/ai_logic.py
import os
import importlib.util
import google.generativeai as genai
from google.generativeai import types
from config import GOOGLE_API_KEY, GEMINI_MODEL, TOOLS_DIR, DATA_DIR

# Initialize Google GenAI
genai.configure(api_key=GOOGLE_API_KEY)

class AIAnalystAgent:
    def __init__(self):
        self.model_name = GEMINI_MODEL
        self.tools = self._discover_tools()
        self.system_instruction = self._build_system_prompt()
        self.chat_session = self._initialize_model()

    def _discover_tools(self) -> list:
        """Scans the tools directory and loads functions to pass to Gemini."""
        loaded_tools =[]
        if not os.path.exists(TOOLS_DIR):
            return loaded_tools

        for folder_name in os.listdir(TOOLS_DIR):
            tool_path = os.path.join(TOOLS_DIR, folder_name)
            main_py_path = os.path.join(tool_path, "main.py")
            
            if os.path.isdir(tool_path) and os.path.exists(main_py_path):
                # Dynamically load the tool module
                spec = importlib.util.spec_from_file_location(f"tool_{folder_name}", main_py_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "execute"):
                    # Add description from MD if available
                    desc_path = os.path.join(tool_path, "description.md")
                    if os.path.exists(desc_path):
                        with open(desc_path, "r", encoding="utf-8") as f:
                            module.execute.__doc__ = f.read()
                            
                    # CRITICAL FIX: Rename the function so Gemini knows its unique name
                    module.execute.__name__ = folder_name
                    loaded_tools.append(module.execute)
                    
        return loaded_tools

    def get_data_context(self, active_dataset_names: list) -> str:
        """Reads metadata from selected datasets in source/data/"""
        context = "Available Active Datasets:\n"
        for ds_name in active_dataset_names:
            ds_path = os.path.join(DATA_DIR, ds_name)
            md_path = os.path.join(ds_path, "metadata.md")
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    context += f"\nDataset '{ds_name}':\n{f.read()}\n"
        return context

    def _build_system_prompt(self) -> str:
        return """You are an expert Data Analyst AI.
1. When asked to write code, provide Python code.
2. MUST write explanations and comments inside the Python code IN VIETNAMESE.
3. If you want to return interactive visualizations, assign them to a variable named `fig` using Plotly.
4. If you have numerical/analytical findings to pass back to yourself or the user, assign them as a string to a variable named `result_data`.
5. Assume pandas is `pd`, numpy is `np`, plotly.express is `px`. Dataframes will be pre-loaded into the namespace with their names defined in metadata.
"""

    def _initialize_model(self):
        """Creates the model instance with native tools and system instructions."""
        # Using Gemini's native features
        model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.tools if self.tools else None,
            system_instruction=self.system_instruction,
        )
        return model.start_chat(history=[])

    def generate_response(self, prompt: str, active_datasets: list, temperature: float = 0.7):
        """
        Sends the prompt to the model. Includes dataset context, 
        handles multi-turn tool execution, and extracts reasoning/thoughts.
        """
        data_context = self.get_data_context(active_datasets)
        full_prompt = f"{data_context}\n\nUser Request: {prompt}"

        generation_config = genai.GenerationConfig(temperature=temperature)

        response = self.chat_session.send_message(
            full_prompt, 
            generation_config=generation_config
        )
        
        # --- NEW: Track executed tools ---
        executed_tools_log =[]
        
        while response.candidates and any(part.function_call for part in response.candidates[0].content.parts):
            part = next(p for p in response.candidates[0].content.parts if p.function_call)
            function_call = part.function_call
            func_name = function_call.name
            func_args = {key: val for key, val in function_call.args.items()}
            
            tool_func = next((t for t in self.tools if t.__name__ == func_name), None)
            
            if tool_func:
                try:
                    tool_result = tool_func(**func_args)
                except Exception as e:
                    tool_result = f"Error executing tool '{func_name}': {str(e)}"
            else:
                tool_result = f"Error: Tool '{func_name}' not found in registry."
                
            # Log the tool call
            executed_tools_log.append({
                "tool": func_name,
                "args": func_args,
                "result": str(tool_result)
            })
                
            response = self.chat_session.send_message(
                content=[{
                    "function_response": {
                        "name": func_name,
                        "response": {"result": tool_result}
                    }
                }],
                generation_config=generation_config
            )

        thought_process = ""
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "thought") and part.thought:
                    thought_process += part.thought + "\n"
                elif hasattr(part, "text") and "thought" in str(part).lower() and not response.text:
                     thought_process += part.text + "\n"

        try:
            text_response = response.text
        except ValueError:
            text_response = "AI did not provide a text response."

        usage = {
            "input_tokens": response.usage_metadata.prompt_token_count,
            "output_tokens": response.usage_metadata.candidates_token_count
        }

        # --- NEW: Return the tools array in the dictionary ---
        return {
            "text": text_response,
            "thought": thought_process.strip() if thought_process else "No explicit reasoning provided by the model.",
            "tools": executed_tools_log,
            "usage": usage,
            "raw_response": response 
        }

    def feed_execution_result(self, result_payload: dict):
        """Feeds the output of execution.py back into the chat history."""
        # This allows the LLM to know the result of the code it just generated
        feedback_text = "Code executed. "
        
        if result_payload["error"]:
            feedback_text += f"\nError occurred:\n{result_payload['error']}"
        else:
            feedback_text += "Success."
            if result_payload["result_data"]:
                feedback_text += f"\n`result_data` output:\n{result_payload['result_data']}"
            if result_payload["stdout"]:
                feedback_text += f"\nConsole stdout:\n{result_payload['stdout']}"
                
        return self.chat_session.send_message(feedback_text)