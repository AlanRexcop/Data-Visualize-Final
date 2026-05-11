# source/services/execution.py
import sys
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from tools.data_utils import describe_df

def execute_code(code_string: str, active_datasets: dict) -> dict:
    """
    Executes the user-approved AI code in a restricted sandbox.
    Expected variables from LLM:
        - `result_data` (for numerical/text outputs back to LLM)
        - `fig` (for interactive Plotly figures)
    """
    # Capture standard output (print statements)
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    # Define the restricted environment
    sandbox_env = {
        "pd": pd,
        "np": np,
        "px": px,
        "go": go,
        "plt": plt, # Included for compatibility, but plotly is preferred
        "describe_df": describe_df
    }
    
    # Inject active dataframes into the execution namespace
    if active_datasets:
        sandbox_env.update(active_datasets)
        
    result_payload = {
        "result_data": None,
        "fig_json": None,
        "stdout": "",
        "error": None
    }

    try:
        # Execute the string as Python code
        exec(code_string, sandbox_env)
        
        # Capture AI-defined outputs
        if "result_data" in sandbox_env:
            result_payload["result_data"] = str(sandbox_env["result_data"])
            
        if "fig" in sandbox_env:
            fig = sandbox_env["fig"]
            # Serialize Plotly fig to JSON for Streamlit rendering
            if hasattr(fig, "to_json"):
                result_payload["fig_json"] = fig.to_json()
                
    except Exception as e:
        result_payload["error"] = str(e)
        
    finally:
        # Always restore standard output
        sys.stdout = old_stdout
        result_payload["stdout"] = redirected_output.getvalue()
        
    return result_payload