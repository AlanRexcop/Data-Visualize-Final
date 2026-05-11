# source/services/ai_logic.py
import os
import importlib.util
import google.generativeai as genai
from google.generativeai.types import content_types
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
                
                # We expect a function named 'execute' in each tool's main.py
                if hasattr(module, "execute"):
                    # Add description from MD if available for better AI context
                    desc_path = os.path.join(tool_path, "description.md")
                    if os.path.exists(desc_path):
                        with open(desc_path, "r", encoding="utf-8") as f:
                            module.execute.__doc__ = f.read()
                            
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
5. Assume pandas is `pd`, numpy is `np`, plotly.express is `px`. Dataframes will be pre-loaded into the namespace with their exact dataset names.
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
        Sends the prompt to the model. Includes dataset context.
        """
        data_context = self.get_data_context(active_datasets)
        full_prompt = f"{data_context}\n\nUser Request: {prompt}"

        # Note: We configure temperature dynamically per request
        generation_config = genai.GenerationConfig(temperature=temperature)

        response = self.chat_session.send_message(
            full_prompt, 
            generation_config=generation_config
        )
        
        # Process usage tokens (Will be passed to the Streamlit UI)
        usage = {
            "input_tokens": response.usage_metadata.prompt_token_count,
            "output_tokens": response.usage_metadata.candidates_token_count
        }

        # Handle native Tool Calls if the model decided to use one
        # In the Google GenAI SDK, function calls are nested within the parts of the response candidates.
        if response.candidates and any(part.function_call for part in response.candidates[0].content.parts):
            # We would handle loop back for tool execution here.
            # For simplicity in this step, we just return the raw response object 
            # to be handled by an orchestrator loop or directly mapped in the UI.
            pass

        # Safely handle text retrieval as .text raises a ValueError if the response contains only function calls.
        try:
            text_response = response.text
        except ValueError:
            text_response = ""

        return {
            "text": text_response,
            "usage": usage,
            "raw_response": response # Retained if we need to extract raw 'thoughts' if API supports it explicitly
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